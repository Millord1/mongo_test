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