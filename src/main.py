from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers.analytics import router as analytics_router
from src.api.routers.customers import router as customers_router
from src.api.routers.orders import router as orders_router
from src.api.routers.products import router as products_router
from src.api.routers.sellers import router as sellers_router
from src.database.mongodb import MongoDB


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application FastAPI."""
    print("Démarrage de FastAPI...")

    try:
        with MongoDB() as db:
            db.command("ping")
            print("🟢 Connexion à MongoDB réussie.")
    except Exception as e:
        print(f"🔴 Erreur de connexion à MongoDB : {e}")

    yield

    print("🛑 Stop FastAPI...")


app = FastAPI(
    title="Olist E-Commerce API",
    description="API légère et performante pour l'exploration du dataset Olist",
    version="1.0.0",
    lifespan=lifespan,
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
