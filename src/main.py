import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers.analytics import router as analytics_router
from src.api.routers.customers import router as customers_router
from src.api.routers.orders import router as orders_router
from src.api.routers.products import router as products_router
from src.api.routers.sellers import router as sellers_router
from src.database.mongodb import MongoDB
from src.ingestion.importer import ensure_csv_files_present
from src.ingestion.mongo_ingester import import_all_collections


def seed_database_if_empty():
    """Point d'entrée d'initialisation au démarrage de FastAPI."""
    try:
        ensure_csv_files_present()
    except Exception as e:
        print(f"🔴 Erreur lors de l'initialisation du dataset : {e}")

    try:
        import_all_collections()
    except Exception as e:
        print(f"🔴 Erreur lors de l'ingestion du dataset : {e}")
        traceback.print_exc()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application FastAPI."""
    print("Démarrage de FastAPI...")

    try:
        with MongoDB() as db:
            db.command("ping")
            print("🟢 Connexion à MongoDB réussie.")

        seed_database_if_empty()

        with MongoDB() as db:
            MongoDB.create_indexes(db)
            print("🟢 Index MongoDB créés.")

    except Exception as e:
        print(f"🔴 Erreur lors de l'initialisation de la base de données : {e}")

    yield

    print("🛑 Stop FastAPI...")


app = FastAPI(
    title="Olist E-Commerce API",
    description="API légère pour l'exploration du dataset Olist",
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
