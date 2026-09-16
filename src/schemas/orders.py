from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(StrEnum):
    DELIVERED = "delivered"
    SHIPPED = "shipped"
    CANCELED = "canceled"
    INVOICED = "invoiced"
    PROCESSING = "processing"
    CREATED = "created"
    APPROVED = "approved"
    UNAVAILABLE = "unavailable"


class OrderResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    id: str = Field(alias="_id")

    customer_id: str
    order_status: OrderStatus

    order_purchase_timestamp: datetime | None = None
    order_approved_at: datetime | None = None
    order_delivered_carrier_date: datetime | None = None
    order_delivered_customer_date: datetime | None = None
    order_estimated_delivery_date: datetime | None = None

    items: list[dict]
    payments: list[dict]
    reviews: list[dict]
