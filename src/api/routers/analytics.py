from typing import Generator

from fastapi import APIRouter, Depends

from src.repositories.analytics_repository import AnalyticsRepository
from src.schemas.analytics import (
    CategoryAnalyticsResponse,
    CustomerAnalyticsResponse,
    GeographyAnalyticsResponse,
    MonthlyMetricsResponse,
    ProductAnalyticsResponse,
    SellerAnalyticsResponse,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


def get_analytics_repository() -> Generator[AnalyticsRepository, None, None]:
    with AnalyticsRepository() as repo:
        yield repo


analytics_repository_dependency = Depends(get_analytics_repository)


@router.get(
    "/monthly-metrics",
    response_model=list[MonthlyMetricsResponse],
    response_model_by_alias=True,
)
def get_monthly_metrics(
    repo: AnalyticsRepository = analytics_repository_dependency,
):
    return repo.get_monthly_metrics()


@router.get(
    "/products",
    response_model=list[ProductAnalyticsResponse],
    response_model_by_alias=True,
)
def get_product_analytics(
    repo: AnalyticsRepository = analytics_repository_dependency,
):
    return repo.get_product_analytics()


@router.get(
    "/categories",
    response_model=list[CategoryAnalyticsResponse],
    response_model_by_alias=True,
)
def get_category_analytics(
    repo: AnalyticsRepository = analytics_repository_dependency,
):
    return repo.get_category_analytics()


@router.get(
    "/sellers",
    response_model=list[SellerAnalyticsResponse],
    response_model_by_alias=True,
)
def get_seller_analytics(
    repo: AnalyticsRepository = analytics_repository_dependency,
):
    return repo.get_seller_analytics()


@router.get(
    "/customers",
    response_model=list[CustomerAnalyticsResponse],
    response_model_by_alias=True,
)
def get_customer_analytics(
    repo: AnalyticsRepository = analytics_repository_dependency,
):
    return repo.get_customer_analytics()


@router.get(
    "/geography",
    response_model=list[GeographyAnalyticsResponse],
    response_model_by_alias=True,
)
def get_geography_analytics(
    repo: AnalyticsRepository = analytics_repository_dependency,
):
    return repo.get_geography_analytics()
