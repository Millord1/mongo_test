from fastapi import APIRouter, Depends, Query

from src.repositories.analytics_repository import AnalyticsRepository
from src.repositories.order_repository import OrderRepository
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


def get_analytics_repository():
    with AnalyticsRepository() as repo:
        yield repo


def get_order_repository():
    with OrderRepository() as repo:
        yield repo


analytics_repository_dependency = Depends(get_analytics_repository)

order_repository_dependency = Depends(get_order_repository)


@router.get(
    "/monthly-metrics",
    response_model=list[MonthlyMetricsResponse],
    response_model_by_alias=True,
)
def get_monthly_metrics(
    limit: int = Query(default=20, ge=1, le=100),
    repo: AnalyticsRepository = analytics_repository_dependency,
):
    return repo.get_monthly_metrics(limit=limit)


@router.get(
    "/products",
    response_model=list[ProductAnalyticsResponse],
    response_model_by_alias=True,
)
def get_product_analytics(
    limit: int = Query(default=20, ge=1, le=100),
    repo: AnalyticsRepository = analytics_repository_dependency,
):
    return repo.get_product_analytics(limit=limit)


@router.get(
    "/categories",
    response_model=list[CategoryAnalyticsResponse],
    response_model_by_alias=True,
)
def get_category_analytics(
    limit: int = Query(default=20, ge=1, le=100),
    repo: AnalyticsRepository = analytics_repository_dependency,
):
    return repo.get_category_analytics(limit=limit)


@router.get(
    "/sellers",
    response_model=list[SellerAnalyticsResponse],
    response_model_by_alias=True,
)
def get_seller_analytics(
    limit: int = Query(default=20, ge=1, le=100),
    repo: AnalyticsRepository = analytics_repository_dependency,
):
    return repo.get_seller_analytics(limit=limit)


@router.get(
    "/customers",
    response_model=list[CustomerAnalyticsResponse],
    response_model_by_alias=True,
)
def get_customer_analytics(
    limit: int = Query(default=20, ge=1, le=100),
    repo: AnalyticsRepository = analytics_repository_dependency,
):
    return repo.get_customer_analytics(limit=limit)


@router.get(
    "/geography",
    response_model=list[GeographyAnalyticsResponse],
    response_model_by_alias=True,
)
def get_geography_analytics(
    limit: int = Query(default=20, ge=1, le=100),
    repo: AnalyticsRepository = analytics_repository_dependency,
):
    return repo.get_geography_analytics(limit=limit)


@router.get("/orders-by-status")
def get_orders_by_status(
    repo: OrderRepository = order_repository_dependency,
):
    return repo.aggregate_orders_by_status()


@router.get("/payments-by-type")
def get_payments_by_type(
    repo: OrderRepository = order_repository_dependency,
):
    return repo.aggregate_payments_by_type()
