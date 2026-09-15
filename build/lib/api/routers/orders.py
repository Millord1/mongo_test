from math import ceil

from fastapi import APIRouter, Depends, Query
from pymongo import MongoClient

from src.api.pagination import PageResponse, PaginationParams

router = APIRouter(prefix="/orders", tags=["Orders"])

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]


@router.get("", response_model=PageResponse[dict])
def get_orders(
    pagination: PaginationParams = Depends(),
    status: str | None = Query(None, description="Filtrer par statut"),
):
    query = {}
    if status:
        query["order_status"] = status

    total = db.orders.count_documents(query)

    cursor = (
        db.orders.find(query)
        .sort("_id", 1)
        .skip(pagination.skip)
        .limit(pagination.size)
    )

    items = list(cursor)

    total_pages = ceil(total / pagination.size) if total > 0 else 1

    return PageResponse(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        total_pages=total_pages,
    )


@router.get("/cursor", response_model=list[dict])
def get_orders_cursor(
    last_id: str | None = Query(
        None, description="ID du dernier document de la page précédente"
    ),
    limit: int = Query(20, ge=1, le=100),
):
    query = {}
    if last_id:
        # Reprend la lecture juste après l'ID fourni
        query["_id"] = {"$gt": last_id}

    cursor = db.orders.find(query).sort("_id", 1).limit(limit)
    return list(cursor)
