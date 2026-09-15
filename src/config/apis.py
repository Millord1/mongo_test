from enum import StrEnum

KAGGLE_DATASET = "olistbr/brazilian-ecommerce"


class DatasetNames(StrEnum):
    customers: str = "olist_customers_dataset.csv"
    sellers: str = "olist_sellers_dataset.csv"
    products: str = "olist_products_dataset.csv"
    category_translation: str = "product_category_name_translation.csv"
    orders: str = "olist_orders_dataset.csv"
    order_items: str = "olist_order_items_dataset.csv"
    order_payments: str = "olist_order_payments_dataset.csv"
    order_reviews: str = "olist_order_reviews_dataset.csv"
