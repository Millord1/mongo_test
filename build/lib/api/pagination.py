from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Numéro de la page (commence à 1)")
    size: int = Field(
        20, ge=1, le=100, description="Nombre d'éléments par page (max 100)"
    )

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.size


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    total_pages: int
