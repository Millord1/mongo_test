# Modélisation MongoDB du projet Olist

## Objectif

Le dataset Olist est initialement composé de plusieurs fichiers CSV reliés
entre eux par des identifiants.

Le choix a été fait de ne pas reproduire directement le modèle relationnel
dans MongoDB. Le modèle documentaire est construit en fonction des usages
de consultation de l'API.

## Collections principales

Le projet utilise quatre collections métier principales :

- `customers`
- `products`
- `sellers`
- `orders`

## Collection `orders`

La collection `orders` contient les informations générales d'une commande :

- identifiant de commande ;
- identifiant client ;
- statut ;
- dates principales.

Les articles, paiements et avis sont directement embarqués dans le document
de la commande sous forme de tableaux :

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

## Analyse avec `explain("executionStats")`

La requête suivante récupère les commandes d'un client triées par date décroissante :

```javascript
db.orders.find({
  customer_id: "9ef432eb6251297304e76186b10a928d"
})
.sort({
  order_purchase_timestamp: -1
})
.explain("executionStats")
```

Avant la création de l'index, MongoDB utilise un `COLLSCAN` et examine **99 441 documents** pour en retourner 1.

```text
totalDocsExamined: 99441
totalKeysExamined: 0
executionTimeMillis: 69
```

Après création de l'index composé :

```javascript
{
  customer_id: 1,
  order_purchase_timestamp: -1
}
```

MongoDB utilise un `IXSCAN` :

```text
totalDocsExamined: 1
totalKeysExamined: 1
executionTimeMillis: 12
```

| Indicateur | Avant | Après |
|---|---:|---:|
| Documents examinés | 99 441 | 1 |
| Temps d'exécution | 69 ms | 12 ms |
| Plan | `COLLSCAN` | `IXSCAN` |

L'index permet donc d'éviter le parcours complet de la collection et réduit fortement le travail effectué par MongoDB.