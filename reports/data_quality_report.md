# Rapport de qualité des données Olist

## 1. Fichiers retenus

| Fichier | Lignes |
|---|---:|
| `olist_customers_dataset.csv` | 99,441 |
| `olist_sellers_dataset.csv` | 3,095 |
| `olist_products_dataset.csv` | 32,951 |
| `product_category_name_translation.csv` | 71 |
| `olist_orders_dataset.csv` | 99,441 |
| `olist_order_items_dataset.csv` | 112,650 |
| `olist_order_payments_dataset.csv` | 103,886 |
| `olist_order_reviews_dataset.csv` | 99,224 |

## 2. Types des colonnes

Les types ci-dessous sont inférés automatiquement par DuckDB à partir des fichiers CSV.

### olist_customers_dataset.csv

| Colonne | Type inféré |
|---|---|
| `customer_id` | `VARCHAR` |
| `customer_unique_id` | `VARCHAR` |
| `customer_zip_code_prefix` | `VARCHAR` |
| `customer_city` | `VARCHAR` |
| `customer_state` | `VARCHAR` |

### olist_sellers_dataset.csv

| Colonne | Type inféré |
|---|---|
| `seller_id` | `VARCHAR` |
| `seller_zip_code_prefix` | `VARCHAR` |
| `seller_city` | `VARCHAR` |
| `seller_state` | `VARCHAR` |

### olist_products_dataset.csv

| Colonne | Type inféré |
|---|---|
| `product_id` | `VARCHAR` |
| `product_category_name` | `VARCHAR` |
| `product_name_lenght` | `BIGINT` |
| `product_description_lenght` | `BIGINT` |
| `product_photos_qty` | `BIGINT` |
| `product_weight_g` | `BIGINT` |
| `product_length_cm` | `BIGINT` |
| `product_height_cm` | `BIGINT` |
| `product_width_cm` | `BIGINT` |

### product_category_name_translation.csv

| Colonne | Type inféré |
|---|---|
| `product_category_name` | `VARCHAR` |
| `product_category_name_english` | `VARCHAR` |

### olist_orders_dataset.csv

| Colonne | Type inféré |
|---|---|
| `order_id` | `VARCHAR` |
| `customer_id` | `VARCHAR` |
| `order_status` | `VARCHAR` |
| `order_purchase_timestamp` | `TIMESTAMP` |
| `order_approved_at` | `TIMESTAMP` |
| `order_delivered_carrier_date` | `TIMESTAMP` |
| `order_delivered_customer_date` | `TIMESTAMP` |
| `order_estimated_delivery_date` | `TIMESTAMP` |

### olist_order_items_dataset.csv

| Colonne | Type inféré |
|---|---|
| `order_id` | `VARCHAR` |
| `order_item_id` | `BIGINT` |
| `product_id` | `VARCHAR` |
| `seller_id` | `VARCHAR` |
| `shipping_limit_date` | `TIMESTAMP` |
| `price` | `DOUBLE` |
| `freight_value` | `DOUBLE` |

### olist_order_payments_dataset.csv

| Colonne | Type inféré |
|---|---|
| `order_id` | `VARCHAR` |
| `payment_sequential` | `BIGINT` |
| `payment_type` | `VARCHAR` |
| `payment_installments` | `BIGINT` |
| `payment_value` | `DOUBLE` |

### olist_order_reviews_dataset.csv

| Colonne | Type inféré |
|---|---|
| `review_id` | `VARCHAR` |
| `order_id` | `VARCHAR` |
| `review_score` | `BIGINT` |
| `review_comment_title` | `VARCHAR` |
| `review_comment_message` | `VARCHAR` |
| `review_creation_date` | `TIMESTAMP` |
| `review_answer_timestamp` | `TIMESTAMP` |


## 3. Valeurs manquantes

### olist_customers_dataset.csv

Aucune valeur manquante détectée.

### olist_sellers_dataset.csv

Aucune valeur manquante détectée.

### olist_products_dataset.csv

| Colonne | Manquantes | % |
|---|---:|---:|
| `product_category_name` | 610 | 1.85% |
| `product_name_lenght` | 610 | 1.85% |
| `product_description_lenght` | 610 | 1.85% |
| `product_photos_qty` | 610 | 1.85% |
| `product_weight_g` | 2 | 0.01% |
| `product_length_cm` | 2 | 0.01% |
| `product_height_cm` | 2 | 0.01% |
| `product_width_cm` | 2 | 0.01% |

### product_category_name_translation.csv

Aucune valeur manquante détectée.

### olist_orders_dataset.csv

| Colonne | Manquantes | % |
|---|---:|---:|
| `order_approved_at` | 160 | 0.16% |
| `order_delivered_carrier_date` | 1,783 | 1.79% |
| `order_delivered_customer_date` | 2,965 | 2.98% |

### olist_order_items_dataset.csv

Aucune valeur manquante détectée.

### olist_order_payments_dataset.csv

Aucune valeur manquante détectée.

### olist_order_reviews_dataset.csv

| Colonne | Manquantes | % |
|---|---:|---:|
| `review_comment_title` | 87,658 | 88.34% |
| `review_comment_message` | 58,256 | 58.71% |

## 4. Doublons sur les clés

| Fichier | Clé | Doublons supplémentaires |
|---|---|---:|
| `olist_customers_dataset.csv` | `customer_id` | 0 |
| `olist_sellers_dataset.csv` | `seller_id` | 0 |
| `olist_products_dataset.csv` | `product_id` | 0 |
| `olist_orders_dataset.csv` | `order_id` | 0 |
| `olist_order_items_dataset.csv` | `order_id + order_item_id` | 0 |
| `olist_order_payments_dataset.csv` | `order_id + payment_sequential` | 0 |

## 5. Intégrité des relations

| Contrôle | Lignes concernées |
|---|---:|
| Orders sans customer | 0 |
| Items sans order | 0 |
| Items sans product | 0 |
| Items sans seller | 0 |
| Payments sans order | 0 |
| Reviews sans order | 0 |

## 6. Cohérence des dates

| Contrôle | Lignes concernées |
|---|---:|
| Approbation avant achat | 0 |
| Transporteur avant achat | 166 |
| Livraison client avant achat | 0 |
| Livraison client avant transporteur | 23 |
| Livraison estimée avant achat | 0 |

## 7. Conclusion

Ce rapport documente les volumes, types de colonnes, valeurs manquantes, doublons, relations entre fichiers et incohérences de dates avant l'import MongoDB.
