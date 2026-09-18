import os

from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.database import Database

load_dotenv(override=False)


class MongoDB:
    def __init__(
        self,
        uri: str | None = None,
        db_name: str | None = None,
    ):
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = db_name or os.getenv("MONGO_DATABASE", "ecommerce_db")
        self.client: MongoClient | None = None
        self.db: Database | None = None

    def __enter__(self) -> Database:
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()

    @staticmethod
    def create_indexes(db: Database):
        db.orders.create_index(
            [("order_status", ASCENDING)],
            name="idx_order_status",
        )

        db.orders.create_index(
            [
                ("customer_id", ASCENDING),
                ("order_purchase_timestamp", DESCENDING),
            ],
            name="idx_customer_purchase_date",
        )
