from math import ceil
from typing import Generator

from fastapi import APIRouter, Depends

from src.api.pagination import OrderQueryParams, PageResponse
from src.repositories.order_repository import OrderRepository
from src.schemas.orders import OrderResponse

from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


def get_order_repository() -> Generator[OrderRepository, None, None]:
    with OrderRepository() as repo:
        yield repo


order_query_params_dependency = Depends()
order_repository_dependency = Depends(get_order_repository)


@router.get(
    "",
    response_model=PageResponse[OrderResponse],
    response_model_by_alias=True,
)
def get_orders(
    params: OrderQueryParams = order_query_params_dependency,
    repo: OrderRepository = order_repository_dependency,
):
    filters = {}

    if params.status:
        filters["order_status"] = params.status

    items, total = repo.get_all_offset(
        skip=params.skip,
        limit=params.size,
        filters=filters,
    )

    total_pages = ceil(total / params.size) if total else 1

    return PageResponse(
        items=items,
        total=total,
        page=params.page,
        size=params.size,
        total_pages=total_pages,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    response_model_by_alias=True,
)
def get_order(
    order_id: str,
    repo: OrderRepository = order_repository_dependency,
):
    order = repo.get_by_id(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Commande introuvable",
        )

    return order


@router.get(
    "/customer/{customer_id}",
    response_model=list[OrderResponse],
    response_model_by_alias=True,
)
def get_orders_by_customer(
    customer_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    repo: OrderRepository = order_repository_dependency,
):
    return repo.get_by_customer_id(
        customer_id=customer_id,
        limit=limit,
    )
