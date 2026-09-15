from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers.orders import router as orders_router
from src.database.mongodb import MongoDB
from src.ingestion.importer import ensure_csv_files_present


def seed_database_if_empty():
    """Point d'entrée d'initialisation au démarrage de FastAPI."""
    try:
        ensure_csv_files_present()
    except Exception as e:
        print(f"🔴 Erreur lors de l'initialisation du dataset : {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application FastAPI."""
    print("Démarrage de FastAPI...")

    try:
        with MongoDB() as db:
            db.command("ping")
            print("🟢 Connexion à MongoDB réussie.")

        seed_database_if_empty()

    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données : {e}")

    yield

    print("🛑 StopFastAPI...")


app = FastAPI(
    title="Olist E-Commerce API",
    description="API légère et performante pour l'exploration du dataset Olist",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(orders_router)


@app.get("/", tags=["Health"])
def health_check():
    """Endpoint de vérification de l'état du service."""
    return {"status": "ok", "message": "API Olist opérationnelle"}
