from math import ceil
from typing import Generator

from fastapi import APIRouter, Depends

from src.api.pagination import OrderQueryParams, PageResponse
from src.repositories.order_repository import OrderRepository

router = APIRouter(prefix="/orders", tags=["Orders"])


def get_order_repository() -> Generator[OrderRepository, None, None]:
    with OrderRepository() as repo:
        yield repo


@router.get("", response_model=PageResponse[dict])
def get_orders(
    params: OrderQueryParams = Depends(),
    repo: OrderRepository = Depends(get_order_repository),
):
    filters = {"order_status": params.status} if params.status else {}

    items, total = repo.get_all_offset(
        skip=params.skip,
        limit=params.size,
        filters=filters,
    )

    total_pages = ceil(total / params.size) if total > 0 else 1

    return PageResponse(
        items=items,
        total=total,
        page=params.page,
        size=params.size,
        total_pages=total_pages,
    )
