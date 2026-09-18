from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from src.api.routers.analytics import router as analytics_router
from src.api.routers.customers import router as customers_router
from src.api.routers.orders import router as orders_router
from src.api.routers.products import router as products_router
from src.api.routers.sellers import router as sellers_router

app = FastAPI(
    title="Olist E-Commerce API",
    description="API légère pour l'exploration du dataset Olist",
    version="1.0.0",
)


@app.exception_handler(PyMongoError)
async def mongo_exception_handler(
    request: Request,
    exc: PyMongoError,
):
    return JSONResponse(
        status_code=503,
        content={"detail": "Service MongoDB temporairement indisponible"},
    )


app.include_router(orders_router)
app.include_router(customers_router)
app.include_router(sellers_router)
app.include_router(products_router)
app.include_router(analytics_router)


@app.get("/", tags=["Health"])
def health_check():
    """Endpoint de vérification de l'état du service."""
    return {"status": "ok", "message": "API Olist opérationnelle"}
