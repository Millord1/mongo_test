from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers.orders import router as orders_router
from src.database.mongodb import MongoDB
from src.repositories.order_repository import OrderRepository


def seed_database_if_empty():
    """Vérifie si la base de données est vide et exécute l'ingestion si nécessaire."""
    with OrderRepository() as repo:
        # Vérification rapide si la collection orders contient au moins 1 document
        if repo.collection.count_documents({}, limit=1) == 0:
            print("⚠️ La base de données est vide. Démarrage du seed initial...")

            # --- APPELLE TES FONCTIONS D'INITIALISATION / DUCKDB ICI ---
            # Exemple :
            # run_ingestion_pipeline()
            # create_indexes()

            print("✅ Initialisation terminée avec succès !")
        else:
            print("ℹ️ Base de données déjà initialisée.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application FastAPI."""
    # 1. Actions au DÉMARRAGE (Startup)
    print("🚀 Démarrage de l'application FastAPI...")

    # Tester/Vérifier la connexion MongoDB
    try:
        with MongoDB() as db:
            db.command("ping")
            print("🟢 Connexion à MongoDB réussie.")

        # Lancer le seeder si nécessaire
        seed_database_if_empty()

    except Exception as e:
        print(f"🔴 Erreur lors de l'initialisation de la base de données : {e}")

    yield  # L'application FastAPI tourne ici et répond aux requêtes

    # 2. Actions à L'ARRÊT (Shutdown)
    print("🛑 Arrêt de l'application FastAPI...")


# Instanciation de l'application FastAPI
app = FastAPI(
    title="Olist E-Commerce API",
    description="API légère et performante pour l'exploration du dataset Olist",
    version="1.0.0",
    lifespan=lifespan,
)

# Enregistrement des routeurs
app.include_router(orders_router)


@app.get("/", tags=["Health"])
def health_check():
    """Endpoint de vérification de l'état du service."""
    return {"status": "ok", "message": "API Olist opérationnelle"}
