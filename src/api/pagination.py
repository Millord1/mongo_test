from typing import Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    total_pages: int


ALLOWED_STATUSES = {
    "delivered",
    "shipped",
    "canceled",
    "invoiced",
    "processing",
    "created",
    "approved",
    "unavailable",
}


class OrderQueryParams(BaseModel):
    page: int = Field(1, ge=1, description="Numéro de la page")
    size: int = Field(20, ge=1, le=100, description="Taille de la page")
    status: str | None = Field(None, description="Filtrer par statut")

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.size

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is None:
            return None
        cleaned = v.strip().lower()
        if cleaned not in ALLOWED_STATUSES:
            raise ValueError(f"Statut invalide : '{v}'")
        return cleaned
