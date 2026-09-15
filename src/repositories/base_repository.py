from typing import Any

from pymongo.database import Database

from src.database.mongodb import MongoDB


class BaseRepository:
    """Classe parente abstraite gérant la connexion et les opérations CRUD de base."""

    collection_name: str
    pk_field: str = "_id"

    def __init__(self, db: Database | None = None):
        self._db = db
        self._mongo_ctx = None

        if self._db is None:
            self._mongo_ctx = MongoDB()
            self._db = self._mongo_ctx.__enter__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._mongo_ctx:
            self._mongo_ctx.__exit__(exc_type, exc_val, exc_tb)
            self._db = None

    @property
    def db(self) -> Database:
        if self._db is None:
            raise RuntimeError("La connexion MongoDB n'est pas initialisée.")
        return self._db

    @property
    def collection(self):
        if not hasattr(self, "collection_name"):
            raise NotImplementedError("La classe enfant doit définir 'collection_name'")
        return self.db[self.collection_name]

    def get_by_id(self, item_id: str) -> dict | None:
        """Récupère un document par sa clé primaire (par défaut _id)."""
        return self.collection.find_one({self.pk_field: item_id})

    def get_all_offset(
        self,
        skip: int,
        limit: int,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[dict], int]:
        """Pagination par Offset + total générique."""
        query = filters or {}
        total = self.collection.count_documents(query)

        cursor = (
            self.collection.find(query).sort(self.pk_field, 1).skip(skip).limit(limit)
        )
        return list(cursor), total

    def get_all_cursor(
        self,
        limit: int,
        last_id: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict]:
        """Pagination par Curseur générique."""
        query = filters or {}
        if last_id:
            query[self.pk_field] = {"$gt": last_id}

        cursor = self.collection.find(query).sort(self.pk_field, 1).limit(limit)
        return list(cursor)
