from math import ceil
from typing import Generator

from fastapi import APIRouter, Depends, Query

from src.api.pagination import PageResponse
from src.repositories.customer_repository import CustomerRepository
from src.schemas.customers import CustomerResponse

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


def get_customer_repository() -> Generator[CustomerRepository, None, None]:
    with CustomerRepository() as repo:
        yield repo


customer_repository_dependency = Depends(get_customer_repository)


@router.get(
    "",
    response_model=PageResponse[CustomerResponse],
    response_model_by_alias=True,
)
def get_customers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    repo: CustomerRepository = customer_repository_dependency,
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
