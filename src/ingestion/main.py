import traceback

from src.database.mongodb import MongoDB
from src.ingestion.mongo_ingester import run_ingestion


def seed_database_if_empty():
    try:
        run_ingestion()
    except Exception as e:
        print(f"🔴 Erreur lors de l'ingestion du dataset : {e}")
        traceback.print_exc()


def main():
    try:
        with MongoDB() as db:
            db.command("ping")
            print("🟢 Connexion à MongoDB réussie.")

        seed_database_if_empty()

        with MongoDB() as db:
            MongoDB.create_indexes(db)
            print("🟢 Index MongoDB créés.")

    except Exception as e:
        print(f"🔴 Erreur de connexion à MongoDB : {e}")


if __name__ == "__main__":
    main()
