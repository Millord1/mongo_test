from enum import StrEnum


class QueryNames(StrEnum):
    CUSTOMERS = "customers"
    SELLERS = "sellers"
    PRODUCTS = "products"

    ORDERS = "orders"
    ORDER_ITEMS = "order_items"
    ORDER_PAYMENTS = "order_payments"
    ORDER_REVIEWS = "order_reviews"

    MONTHLY_METRICS = "monthly_metrics"
    PRODUCT_ANALYTICS = "product_analytics"
    CATEGORY_ANALYTICS = "category_analytics"
    SELLER_ANALYTICS = "seller_analytics"
    CUSTOMER_ANALYTICS = "customer_analytics"
    GEOGRAPHY_ANALYTICS = "geography_analytics"
