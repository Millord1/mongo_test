from math import ceil
from typing import Generator

from fastapi import APIRouter, Depends, Query

from src.api.pagination import PageResponse
from src.repositories.seller_repository import SellerRepository
from src.schemas.sellers import SellerResponse

router = APIRouter(
    prefix="/sellers",
    tags=["Sellers"],
)


def get_seller_repository() -> Generator[SellerRepository, None, None]:
    with SellerRepository() as repo:
        yield repo


seller_repository_dependency = Depends(get_seller_repository)


@router.get(
    "",
    response_model=PageResponse[SellerResponse],
    response_model_by_alias=True,
)
def get_sellers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    repo: SellerRepository = seller_repository_dependency,
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
