# Plan de correction des API et des analytiques

## Objectif

Rétablir les réponses HTTP de toutes les routes de lecture, avec des modèles Pydantic valides et un contrat JSON stable. Les documents MongoDB conservent leur clé `_id` dans la réponse publique. Les requêtes analytiques SQL sont corrigées puis les collections sont réimportées.

## Constats

1. Les documents analytiques et dimensionnels sont importés avec leur identifiant métier dans `_id` (`src/ingestion/mongo_ingester.py:78-84`).
2. Les routes analytiques ne déclarent aucun `response_model` (`src/api/routers/analytics.py:18-65`). Ajouter les modèles actuels sans alias échoue pour les champs métier attendus (`product_id`, `seller_id`, `customer_id`, `category`, `state`, `month`).
3. Les routes paginées produits, vendeurs et clients utilisent déjà des `response_model`, mais leurs schemas attendent un champ métier alors que MongoDB renvoie `_id` (`src/api/routers/products.py:21-24`, `src/api/routers/sellers.py:21-24`, `src/api/routers/customers.py:21-24`).
4. Les produits, catégories et clients sans commande peuvent produire des agrégats `NULL`. Les champs numériques obligatoires actuels (`revenue`, `units_sold`, `avg_order_value`, `avg_order_value`) provoquent une erreur de validation Pydantic.
5. `first_order` et `last_order` sont des timestamps mais sont typés `object | None` (`src/schemas/analytics.py:59-60`).
6. `page` et `size` ne sont pas validés sur les routes produits, vendeurs et clients ; `size=0` peut provoquer une division par zéro lors du calcul de `total_pages`.
7. Les requêtes SQL actuelles joignent directement les lignes de commandes, d'articles et d'avis. Cela pondère les moyennes par le nombre d'articles/avis et peut multiplier les revenus. Les AOV ne sont pas des revenus divisés par le nombre de commandes.

## Décisions déjà prises

- Conserver `_id` dans le JSON public.
- Représenter les entités sans vente avec les compteurs et revenus à zéro, et les moyennes à `null`.
- Corriger à la fois la couche API et les requêtes SQL.
- Inclure tous les vendeurs, y compris ceux sans vente.
- Définir `revenue` et `total_spent` comme prix des articles + fret. Le fret reste également disponible dans `freight` / `freight_revenue`. Les AOV utilisent cette valeur totale divisée par le nombre de commandes distinctes.

## Travaux d'implémentation

### 1. Corriger les schemas de réponse

Dans `src/schemas/analytics.py` :

- mapper chaque identifiant métier sur `_id` avec un alias de validation et de sérialisation :
  - `month` pour les métriques mensuelles ;
  - `product_id`, `seller_id`, `customer_id` pour les analytiques correspondantes ;
  - `id` pour les catégories et la géographie, afin de conserver `_id` dans le JSON.
- typer `first_order` et `last_order` en `datetime | None`.
- rendre les moyennes sans donnée optionnelles (`float | None`) et prévoir des valeurs par défaut cohérentes pour les compteurs/revenus normalisés à zéro.
- ajouter `ConfigDict(populate_by_name=True)` si les modèles doivent aussi accepter temporairement les noms métier lors des tests ou d'une future évolution.

Dans `src/schemas/products.py`, `src/schemas/sellers.py` et `src/schemas/customers.py` :

- mapper respectivement `product_id`, `seller_id` et `customer_id` sur `_id`.
- conserver les champs optionnels existants et leurs valeurs par défaut.

Dans `src/schemas/orders.py` :

- conserver l'alias `_id` et utiliser ce modèle dans la route des commandes afin de remplacer `PageResponse[dict]` par un contrat typé.

### 2. Corriger les routes API

Dans `src/api/routers/analytics.py` :

- importer les six modèles analytiques.
- déclarer `response_model=list[...]` sur chaque route.
- déclarer explicitement `response_model_by_alias=True` pour garantir que `_id` reste la clé JSON publique.
- trier les résultats analytiques par `_id` pour des réponses déterministes.

Dans `src/api/routers/products.py`, `src/api/routers/sellers.py`, `src/api/routers/customers.py` et `src/api/routers/orders.py` :

- déclarer explicitement `response_model_by_alias=True`.
- valider `page >= 1` et `1 <= size <= 100` avec `fastapi.Query`.
- utiliser `PageResponse[OrderResponse]` pour `/orders`.
- conserver le calcul de pagination existant une fois `size` garanti non nul.

### 3. Normaliser les documents analytiques côté repository

Dans `src/repositories/analytics_repository.py` :

- centraliser une normalisation défensive des valeurs agrégées.
- convertir les compteurs/revenus absents en zéro.
- conserver `null` pour les moyennes sans donnée.
- convertir les timestamps déjà BSON en valeurs compatibles avec `datetime`.
- ajouter un tri `_id` ascendant à toutes les collections analytiques.
- ne pas transformer `_id` en champ métier, conformément au contrat choisi.

Cette normalisation protège aussi les endpoints contre d'anciennes collections importées avant la correction SQL.

### 4. Corriger les requêtes SQL analytiques

Dans `src/sql/monthly_metrics.sql` :

- agréger d'abord les articles par commande, puis joindre une seule ligne d'avis par commande.
- calculer `revenue` avec `SUM(price + freight_value)`.
- conserver `freight` séparément.
- calculer `avg_order_value` comme revenu total / nombre de commandes distinctes.
- calculer les délais et les notes au niveau commande, sans pondération par les articles.

Dans `src/sql/product_analytics.sql` :

- pré-agréger les articles par produit.
- faire un `LEFT JOIN` depuis `products` pour conserver les produits sans vente.
- mettre les compteurs et revenus à zéro, et `avg_price` à `null` sans vente.
- calculer `revenue` avec prix + fret.

Dans `src/sql/category_analytics.sql` :

- utiliser la catégorie anglaise avec repli sur la catégorie originale.
- pré-agréger ou compter uniquement les lignes d'articles pour éviter de compter les produits sans vente comme une unité.
- conserver toutes les catégories, avec zéros et moyennes nulles si nécessaire.
- calculer `revenue` avec prix + fret.

Dans `src/sql/seller_analytics.sql` :

- partir de `sellers` et faire un `LEFT JOIN` vers les faits vendeur-commande.
- agréger les articles au niveau `(seller_id, order_id)` avant de calculer les moyennes.
- inclure les vendeurs sans vente avec zéros et moyennes nulles.
- calculer `avg_order_value` comme `(prix + fret) / commandes distinctes`.

Dans `src/sql/customer_analytics.sql` :

- partir de `customers` et conserver les clients sans commande.
- agréger les articles par commande avant le calcul.
- calculer `total_spent` et `avg_order_value` avec prix + fret.
- conserver `first_order` et `last_order` comme timestamps, ou `null` sans commande.

Dans `src/sql/geography_analytics.sql` :

- agréger les commandes au niveau commande avant le regroupement par état.
- calculer `revenue` avec prix + fret.
- calculer le délai moyen par commande, sans pondération par les articles.
- conserver les états sans commande avec des revenus à zéro et une moyenne nulle.

Ne pas modifier le mécanisme d'import lui-même : après les changements SQL, le pipeline existant remplacera les collections analytiques.

### 5. Ajouter des tests de contrat

Dans `tests/` :

- tester la validation de chaque modèle avec un document MongoDB contenant `_id`.
- tester les documents sans vente : zéros pour les compteurs/revenus, `null` pour les moyennes.
- tester la sérialisation FastAPI et vérifier que les réponses contiennent `_id` plutôt qu'un champ métier d'ID.
- tester les routes analytiques avec des dépendances de repository remplacées par des données fictives.
- tester `/products`, `/sellers`, `/customers` et `/orders` avec une page valide.
- tester `size=0`, `page=0` et les pages hors limite : réponse HTTP 422, jamais 500.
- tester les réponses de commandes avec le modèle `OrderResponse`.

## Validation

1. Exécuter les tests ajoutés.
2. Exécuter `ruff check src` et la compilation Python.
3. Relancer l'ingestion MongoDB avec le pipeline existant afin de reconstruire les collections à partir des SQL corrigés.
4. Démarrer FastAPI et appeler chaque endpoint listé ci-dessus.
5. Vérifier :
   - statut HTTP 200 ;
   - JSON sérialisable sans `ResponseValidationError` ;
   - présence de `_id` dans les réponses ;
   - zéros et `null` corrects sur les entités sans vente ;
   - cohérence des revenus et AOV avec la règle prix + fret ;
   - statut 422 pour les paramètres de pagination invalides.

## Risques et garde-fous

- Ne pas utiliser `Field(validation_alias="_id")` seul si le contrat public doit conserver `_id` : configurer explicitement l'alias de sérialisation ou activer `response_model_by_alias=True`.
- Ne pas compter les lignes de jointure directement pour les moyennes : pré-agréger au niveau commande.
- Ne pas remplacer les `NULL` de moyennes par zéro dans les SQL ou les schemas ; seul le contrat décidé impose zéro pour les compteurs/revenus.
- Le pipeline d'ingestion remplace les collections : la validation doit être faite après réimport, pas uniquement avec les anciens documents.
