from math import ceil
from typing import Generator

from fastapi import APIRouter, Depends, Query

from src.api.pagination import PageResponse
from src.repositories.product_repository import ProductRepository
from src.schemas.products import ProductResponse

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


def get_product_repository() -> Generator[ProductRepository, None, None]:
    with ProductRepository() as repo:
        yield repo


product_repository_dependency = Depends(get_product_repository)


@router.get(
    "",
    response_model=PageResponse[ProductResponse],
    response_model_by_alias=True,
)
def get_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    repo: ProductRepository = product_repository_dependency,
):
    skip = (page - 1) * size

    items, total = repo.get_all_offset(
        skip=skip,
        limit=size,
    )

    return PageResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        total_pages=ceil(total / size) if total else 1,
    )
