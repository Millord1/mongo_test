from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from src.schemas.orders import OrderStatus

T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    total_pages: int


class OrderQueryParams(BaseModel):
    page: int = Field(1, ge=1, description="Numéro de la page")
    size: int = Field(20, ge=1, le=100, description="Taille de la page")
    status: OrderStatus | None = Field(
        default=None,
        alias="order_status",
        description="Filtrer par statut",
    )

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.size
