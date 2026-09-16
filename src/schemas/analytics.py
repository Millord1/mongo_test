from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MonthlyMetricsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    month: datetime = Field(alias="_id")
    orders: int = 0
    delivered_orders: int = 0
    cancelled_orders: int = 0
    revenue: float = 0.0
    freight: float = 0.0
    avg_order_value: float | None = None
    avg_delivery_days: float | None = None
    avg_review_score: float | None = None


class ProductAnalyticsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_id: str = Field(alias="_id")
    product_category_name: str | None = None
    product_category_name_english: str | None = None
    total_orders: int = 0
    units_sold: int = 0
    revenue: float = 0.0
    freight_revenue: float = 0.0
    avg_price: float | None = None
    unique_sellers: int = 0


class CategoryAnalyticsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    category_english: str | None = None
    orders: int = 0
    units_sold: int = 0
    revenue: float = 0.0
    freight_revenue: float = 0.0
    avg_price: float | None = None


class SellerAnalyticsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    seller_id: str = Field(alias="_id")
    orders: int = 0
    revenue: float = 0.0
    freight_revenue: float = 0.0
    avg_order_value: float | None = None
    avg_delivery_days: float | None = None
    delivered_orders: int = 0


class CustomerAnalyticsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="_id")
    customer_unique_id: str
    customer_zip_code_prefix: int
    customer_city: str
    customer_state: str
    orders: int = 0
    total_spent: float = 0.0
    avg_order_value: float | None = None
    first_order: datetime | None = None
    last_order: datetime | None = None


class GeographyAnalyticsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    unique_customers: int = 0
    orders: int = 0
    revenue: float = 0.0
    avg_delivery_days: float | None = None
