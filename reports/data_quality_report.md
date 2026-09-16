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

## 2. Valeurs manquantes

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

## 3. Doublons sur les clés

| Fichier | Clé | Doublons supplémentaires |
|---|---|---:|
| `olist_customers_dataset.csv` | `customer_id` | 0 |
| `olist_sellers_dataset.csv` | `seller_id` | 0 |
| `olist_products_dataset.csv` | `product_id` | 0 |
| `olist_orders_dataset.csv` | `order_id` | 0 |
| `olist_order_items_dataset.csv` | `order_id + order_item_id` | 0 |
| `olist_order_payments_dataset.csv` | `order_id + payment_sequential` | 0 |

## 4. Intégrité des relations

| Contrôle | Lignes concernées |
|---|---:|
| Orders sans customer | 0 |
| Items sans order | 0 |
| Items sans product | 0 |
| Items sans seller | 0 |
| Payments sans order | 0 |
| Reviews sans order | 0 |

## 5. Cohérence des dates

| Contrôle | Lignes concernées |
|---|---:|
| Approbation avant achat | 0 |
| Transporteur avant achat | 166 |
| Livraison client avant achat | 0 |
| Livraison client avant transporteur | 23 |
| Livraison estimée avant achat | 0 |

## 6. Conclusion

Ce rapport documente les volumes, valeurs manquantes, doublons, relations entre fichiers et incohérences de dates avant l'import MongoDB.
