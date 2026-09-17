# Olist — MongoDB & FastAPI

## Présentation

Ce projet exploite le dataset e-commerce **Olist** afin de construire une solution MongoDB cohérente et de l'exposer à travers une API REST développée avec FastAPI.

L'objectif n'est pas simplement de transférer les fichiers CSV dans MongoDB. Le projet cherche à :

- analyser la qualité et les relations des données sources ;
- construire un modèle documentaire adapté aux usages de consultation ;
- automatiser la préparation et l'import des données ;
- exposer plusieurs ressources à travers une API REST ;
- produire des résultats analytiques utiles ;
- contrôler les volumes retournés par l'API ;
- valider les paramètres utilisateurs et gérer les erreurs ;
- analyser les performances d'une requête MongoDB avec `explain()` ;
- améliorer cette requête grâce à un index adapté ;
- fournir un projet reproductible et exécutable depuis le dépôt Git.

Technologies principales :

| Technologie | Utilisation |
|---|---|
| Python 3.12 | développement du projet |
| MongoDB | stockage documentaire |
| PyMongo | communication Python / MongoDB |
| FastAPI | API REST |
| Pydantic | validation et sérialisation |
| DuckDB | lecture, préparation et analyse des données |
| Docker | conteneurisation |
| Docker Compose | orchestration des services |
| Ruff | contrôle de la qualité du code |
| unittest | tests automatisés |

---

# Installation depuis le dépôt Git

La méthode recommandée consiste à utiliser Docker.

## 1. Prérequis

Installer :

- Git ;
- Docker Desktop ;
- Docker Compose.

Vérifier l'installation :

```bash
git --version
docker --version
docker compose version
```

---

## 2. Cloner le dépôt

```bash
git clone https://github.com/Millord1/mongo_test.git
cd mongo_test
```

---

## 3. Créer le fichier d'environnement

Le dépôt contient :

```text
.env.example
```

Il sert de modèle pour créer le véritable fichier `.env`.

Sous PowerShell :

```powershell
Copy-Item .env.example .env
```

Sous Bash :

```bash
cp .env.example .env
```

Le fichier contient notamment :

```env
KAGGLE_USERNAME=
KAGGLE_KEY=

MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=rootpassword

MONGO_DATABASE=ecommerce_db
MONGO_URI=mongodb://root:rootpassword@mongodb:27017/?authSource=admin
```

Renseigner les identifiants Kaggle nécessaires dans :

```text
KAGGLE_USERNAME
KAGGLE_KEY
```

Le véritable fichier `.env` est ignoré par Git et ne doit jamais être versionné.

---

## 4. Construire et lancer le projet

Depuis la racine du dépôt :

```bash
docker compose -f docker/docker-compose.yml up --build
```

Docker Compose démarre automatiquement les différents composants du projet.

Le déroulement est le suivant :

```text
MongoDB
   │
   │ healthcheck OK
   ▼
Ingestion
   │
   │ préparation + import
   │ création des index
   │ exit code 0
   ▼
FastAPI
```

Lorsque l'import est terminé, l'API démarre automatiquement.

---

## 5. Accéder à l'API

API :

```text
http://localhost:8000
```

Documentation Swagger :

```text
http://localhost:8000/docs
```

La page Swagger permet de consulter et de tester directement les différentes routes de l'API.

---

## 6. Arrêter le projet

```bash
docker compose -f docker/docker-compose.yml down
```

Les données MongoDB sont stockées dans un volume Docker nommé.

Un simple `docker compose down` arrête donc les conteneurs sans supprimer les données persistées.

Pour supprimer également le volume MongoDB :

```bash
docker compose -f docker/docker-compose.yml down -v
```

---

# Installation locale sans Docker

Docker reste la méthode recommandée, mais les dépendances Python peuvent également être installées localement.

Le projet utilise Python 3.12.

Créer un environnement virtuel :

```bash
python -m venv env
```

Sous PowerShell :

```powershell
.\env\Scripts\Activate.ps1
```

Puis installer le projet et les dépendances de développement :

```bash
pip install -e ".[dev]"
```

Les dépendances sont déclarées dans :

```text
pyproject.toml
```

Ce fichier joue ici le rôle de manifeste de dépendances du projet.

---

# Dataset Olist

Le dataset Olist contient environ 100 000 commandes e-commerce réalisées au Brésil entre 2016 et 2018.

Le projet exploite plusieurs fichiers liés entre eux, notamment :

```text
customers
orders
order_items
order_payments
order_reviews
products
sellers
geolocation
product_category_name_translation
```

Les principales relations utilisent les identifiants :

```text
customer_id
order_id
product_id
seller_id
```

Le projet utilise donc largement plus que les cinq fichiers liés demandés dans le brief.

Avant leur stockage dans MongoDB, les fichiers sont lus et préparés avec Python et DuckDB.

---

# Analyse de la qualité des données

Une étape d'analyse des données sources est disponible dans :

```text
src/analysis/data_quality.py
```

Elle permet notamment de contrôler :

- le nombre de lignes des fichiers ;
- les types de colonnes inférés par DuckDB ;
- les valeurs manquantes ;
- les doublons ;
- les relations orphelines entre certains fichiers ;
- certaines incohérences de dates.

Exécution :

```bash
python -m src.analysis.data_quality
```

Le rapport produit est enregistré dans :

```text
reports/data_quality_report.md
```

Cette étape permet de comprendre les données avant leur transformation en documents MongoDB.

---

# Modélisation MongoDB

## Pourquoi ne pas reproduire le modèle relationnel ?

Les fichiers Olist ressemblent initialement à des tables relationnelles.

Une solution simple aurait été de créer une collection MongoDB pour chaque fichier CSV.

Ce choix n'a pas été retenu.

MongoDB étant une base documentaire, la modélisation a été construite en fonction des usages de consultation de l'API et non en recopiant mécaniquement la structure des fichiers.

---

## Collections métier principales

Le modèle utilise principalement quatre collections :

```text
customers
products
sellers
orders
```

La collection `orders` constitue le document métier principal.

---

## Structure d'une commande

Exemple simplifié :

```json
{
  "_id": "order_id",
  "customer_id": "customer_id",
  "order_status": "delivered",
  "order_purchase_timestamp": "...",
  "items": [],
  "payments": [],
  "reviews": []
}
```

Les fichiers :

```text
order_items
order_payments
order_reviews
```

sont intégrés directement dans les documents `orders`.

Ces données sont fortement dépendantes de la commande et sont fréquemment consultées avec elle.

L'embarquement permet donc de récupérer une commande complète sans multiplier les accès à plusieurs collections.

---

## Références

Les entités réutilisées par plusieurs commandes restent dans des collections séparées :

```text
customers
products
sellers
```

Les documents de commande conservent notamment les identifiants :

```text
customer_id
product_id
seller_id
```

Le modèle combine donc :

```text
embedding   → données appartenant directement à la commande
références  → entités partagées par plusieurs commandes
```

Cette approche permet de limiter la duplication tout en profitant du modèle documentaire MongoDB.

---

## Catégories produit

Le fichier :

```text
product_category_name_translation
```

n'est pas conservé sous forme d'une collection indépendante.

La traduction utile est directement intégrée aux produits lors de la préparation des données.

---

# Import des données

Le processus principal d'ingestion est situé dans :

```text
src/ingestion/mongo_ingester.py
```

Les requêtes de préparation sont notamment stockées dans :

```text
src/sql/
```

Le processus :

```text
fichiers Olist
      │
      ▼
DuckDB / SQL
      │
      ▼
préparation Python
      │
      ▼
documents MongoDB
      │
      ▼
création des index
```

L'ingestion est exécutée automatiquement par le service Docker :

```text
ingest
```

Le service attend que MongoDB soit déclaré `healthy` avant de commencer.

L'API attend ensuite que l'ingestion se termine correctement.

Cela évite que FastAPI démarre alors que les données ne sont pas encore disponibles.

---

# Architecture applicative

L'architecture de consultation est la suivante :

```text
Client
  │
  │ requête HTTP
  ▼
FastAPI
  │
  ▼
Router
  │
  ▼
Repository
  │
  ▼
PyMongo
  │
  ▼
MongoDB
  │
  ▼
Document / agrégation
  │
  ▼
FastAPI
  │
  ▼
JSON
```

Les routers FastAPI sont responsables de l'interface HTTP.

Les repositories regroupent les accès MongoDB.

Les schemas Pydantic définissent et valident les données exposées par l'API.

---

# Pourquoi passer par une API ?

Les utilisateurs de l'application n'accèdent pas directement à MongoDB.

FastAPI fournit une couche intermédiaire qui permet :

- de contrôler les données accessibles ;
- de valider les paramètres reçus ;
- de contrôler la taille des réponses ;
- de gérer les erreurs de façon cohérente ;
- de centraliser la logique d'accès aux données ;
- de fournir une documentation OpenAPI/Swagger.

Le client n'a donc pas besoin de connaître la structure interne de MongoDB.

---

# API REST

Quelques routes principales :

| Méthode | Route | Description |
|---|---|---|
| GET | `/` | état de l'API |
| GET | `/orders` | liste paginée des commandes |
| GET | `/orders/{order_id}` | consultation d'une commande |
| GET | `/orders/customer/{customer_id}` | commandes d'un client |
| GET | `/customers` | liste des clients |
| GET | `/products` | liste des produits |
| GET | `/sellers` | liste des vendeurs |
| GET | `/analytics/orders-by-status` | répartition des commandes par statut |
| GET | `/analytics/payments-by-type` | statistiques des paiements par type |

D'autres routes analytiques sont disponibles.

La liste exacte des routes, paramètres et modèles de réponse est consultable dans Swagger :

```text
http://localhost:8000/docs
```

---

# Pagination et contrôle des volumes

Les collections Olist peuvent contenir plusieurs dizaines de milliers de documents.

Il serait donc risqué de retourner toute une collection dans une seule réponse HTTP.

Les routes de consultation utilisent une pagination ou une limite de résultats.

Les paramètres concernés sont validés par FastAPI et Pydantic.

Pour les routes utilisant `limit`, la valeur maximale autorisée est :

```text
100
```

Par exemple, une valeur supérieure à la limite est rejetée avec :

```text
HTTP 422
```

Le contrôle des volumes protège donc à la fois l'API et le client contre des réponses inutilement volumineuses.

---

# Gestion des erreurs

L'API renvoie des codes HTTP cohérents.

## Ressource inexistante

Exemple :

```text
GET /orders/{order_id}
```

Si la commande n'existe pas :

```text
404 Not Found
```

Réponse :

```json
{
  "detail": "Commande introuvable"
}
```

---

## Paramètre invalide

Les contraintes FastAPI/Pydantic provoquent une réponse :

```text
422 Unprocessable Entity
```

Par exemple si une limite dépasse la valeur maximale autorisée.

---

## MongoDB indisponible

Les erreurs PyMongo sont interceptées par l'application.

Réponse :

```text
503 Service Unavailable
```

```json
{
  "detail": "Service MongoDB temporairement indisponible"
}
```

La connexion MongoDB utilise également un timeout afin d'éviter qu'une requête reste bloquée trop longtemps lorsque MongoDB est indisponible.

---

# Agrégations MongoDB

Le projet contient plusieurs traitements analytiques.

Certaines données analytiques sont préparées lors de l'ingestion avec DuckDB.

Deux routes utilisent également de véritables pipelines `aggregate()` exécutés directement par MongoDB.

---

## Commandes par statut

Route :

```text
GET /analytics/orders-by-status
```

Pipeline simplifié :

```javascript
[
  {
    "$group": {
      "_id": "$order_status",
      "order_count": {
        "$sum": 1
      }
    }
  },
  {
    "$sort": {
      "order_count": -1
    }
  },
  {
    "$project": {
      "_id": 0,
      "status": "$_id",
      "order_count": 1
    }
  }
]
```

Cette agrégation permet d'obtenir le nombre de commandes pour chaque statut.

---

## Paiements par type

Route :

```text
GET /analytics/payments-by-type
```

Pipeline :

```javascript
[
  {
    "$unwind": "$payments"
  },
  {
    "$group": {
      "_id": "$payments.payment_type",
      "payment_count": {
        "$sum": 1
      },
      "total_amount": {
        "$sum": "$payments.payment_value"
      },
      "average_amount": {
        "$avg": "$payments.payment_value"
      }
    }
  },
  {
    "$sort": {
      "total_amount": -1
    }
  },
  {
    "$project": {
      "_id": 0,
      "payment_type": "$_id",
      "payment_count": 1,
      "total_amount": {
        "$round": ["$total_amount", 2]
      },
      "average_amount": {
        "$round": ["$average_amount", 2]
      }
    }
  }
]
```

Le résultat fournit notamment :

```text
type de paiement
nombre de paiements
montant total
montant moyen
```

Ces calculs sont exécutés directement par MongoDB.

---

# Analyse des performances MongoDB

Une requête utilisée par l'API recherche les commandes d'un client et les trie de la plus récente à la plus ancienne.

```javascript
db.orders.find({
  customer_id: "9ef432eb6251297304e76186b10a928d"
})
.sort({
  order_purchase_timestamp: -1
})
```

La requête a été analysée avec :

```javascript
.explain("executionStats")
```

---

## Avant création de l'index

Le plan d'exécution utilise :

```text
COLLSCAN
```

Valeurs observées :

```text
totalDocsExamined: 99441
totalKeysExamined: 0
executionTimeMillis: 69
```

MongoDB parcourt donc **99 441 documents pour obtenir 1 résultat**.

---

## Index choisi

L'API filtre sur :

```text
customer_id
```

puis trie sur :

```text
order_purchase_timestamp DESC
```

Un index composé correspondant à cet usage a donc été créé :

```javascript
db.orders.createIndex(
  {
    customer_id: 1,
    order_purchase_timestamp: -1
  },
  {
    name: "idx_customer_purchase_date"
  }
)
```

L'index est également créé automatiquement pendant l'ingestion.

---

## Après création de l'index

MongoDB utilise désormais :

```text
IXSCAN
```

Valeurs observées :

```text
totalDocsExamined: 1
totalKeysExamined: 1
executionTimeMillis: 12
```

Comparaison :

| Indicateur | Sans index | Avec index |
|---|---:|---:|
| Documents examinés | 99 441 | 1 |
| Clés examinées | 0 | 1 |
| Temps observé | 69 ms | 12 ms |
| Plan | `COLLSCAN` | `IXSCAN` |

L'amélioration la plus significative est le nombre de documents examinés :

```text
99 441 → 1
```

Les temps d'exécution dépendent de la machine, du cache et de l'état du serveur MongoDB. Ils représentent donc uniquement les valeurs observées lors du test.

---

# Tests automatisés

Les tests sont situés dans :

```text
tests/test_api_responses.py
```

Ils vérifient notamment :

- la sérialisation des identifiants MongoDB ;
- la normalisation des résultats analytiques ;
- les contrats de réponse des routes ;
- la validation des paramètres ;
- le rejet d'une limite supérieure à 100 ;
- la réponse `404` pour une commande inexistante ;
- la réponse `503` lorsqu'une erreur MongoDB se produit.

Exécution :

```bash
python -m unittest discover -s tests -v
```

État actuel :

```text
Ran 11 tests
OK
```

---

# Qualité du code

Le projet utilise Ruff.

Vérification :

```bash
ruff check src tests
```

Résultat attendu :

```text
All checks passed!
```

Formatage :

```bash
ruff format src tests
```

---

# Structure du dépôt

```text
mongo_test/
│
├── .dockerignore
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── reports/
│   └── data_quality_report.md
│
├── src/
│   ├── analysis/
│   │   └── data_quality.py
│   │
│   ├── api/
│   │   ├── pagination.py
│   │   └── routers/
│   │       ├── analytics.py
│   │       ├── customers.py
│   │       ├── orders.py
│   │       ├── products.py
│   │       └── sellers.py
│   │
│   ├── config/
│   │   ├── apis.py
│   │   └── sql.py
│   │
│   ├── database/
│   │   ├── duckdb.py
│   │   └── mongodb.py
│   │
│   ├── ingestion/
│   │   ├── importer.py
│   │   └── mongo_ingester.py
│   │
│   ├── repositories/
│   ├── schemas/
│   ├── sql/
│   └── main.py
│
└── tests/
    └── test_api_responses.py
```

---

# Reproductibilité

Le projet contient les éléments nécessaires à sa reconstruction :

```text
code source
pyproject.toml
.env.example
Dockerfile
docker-compose.yml
scripts d'ingestion
scripts SQL
tests
rapport de qualité
```

Les secrets réels ne sont pas versionnés.

Le lancement :

```bash
docker compose -f docker/docker-compose.yml up --build
```

permet de reconstruire l'application, démarrer MongoDB, importer les données, créer les index puis démarrer FastAPI.

---

# Organisation Git

Le projet est versionné avec Git.

Les fichiers générés ou sensibles sont exclus du dépôt, notamment :

```text
.env
env/
__pycache__/
*.pyc
*.egg-info/
data/
```

L'historique Git permet également d'identifier les contributions réalisées par les différents membres du projet.

Pour afficher les contributions :

```bash
git shortlog -sn --all
```

---

# Documentation

La documentation interactive de l'API est générée automatiquement par FastAPI/OpenAPI :

```text
http://localhost:8000/docs
```

Le rapport d'analyse des données est disponible dans :

```text
reports/data_quality_report.md
```

Le présent README documente :

```text
installation
architecture
modélisation MongoDB
ingestion
API
agrégations
validation
gestion des erreurs
index
explain()
tests
reproductibilité
```

---

# Résumé du fonctionnement

Le fonctionnement global peut être résumé ainsi :

```text
Dataset Olist
      │
      ▼
Analyse / DuckDB
      │
      ▼
Transformation des données
      │
      ▼
MongoDB
      │
      ▼
Repositories Python
      │
      ▼
FastAPI
      │
      ▼
API JSON / Swagger
```

MongoDB assure le stockage documentaire et les agrégations.

FastAPI fournit une interface HTTP contrôlée permettant aux utilisateurs et applications clientes d'accéder aux données sans se connecter directement à la base.