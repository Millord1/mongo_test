from src.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository):
    collection_name = "orders"
    pk_field = "_id"

    def get_by_customer_id(self, customer_id: str, limit: int = 20) -> list[dict]:
        """Requête métier spécifique : historique des commandes d'un client."""
        cursor = (
            self.collection.find({"customer_id": customer_id})
            .sort("order_purchase_timestamp", -1)
            .limit(limit)
        )
        return list(cursor)
