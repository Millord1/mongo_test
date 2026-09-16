from src.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository):
    collection_name = "orders"
    pk_field = "_id"

    def get_by_customer_id(
        self,
        customer_id: str,
        limit: int = 20,
    ) -> list[dict]:
        cursor = (
            self.collection.find({"customer_id": customer_id})
            .sort(
                "order_purchase_timestamp",
                -1,
            )
            .limit(limit)
        )

        return list(cursor)

    def aggregate_orders_by_status(self) -> list[dict]:
        pipeline = [
            {
                "$group": {
                    "_id": "$order_status",
                    "order_count": {"$sum": 1},
                }
            },
            {
                "$sort": {
                    "order_count": -1,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "status": "$_id",
                    "order_count": 1,
                }
            },
        ]

        return list(self.collection.aggregate(pipeline))

    def aggregate_payments_by_type(self) -> list[dict]:
        pipeline = [
            {"$unwind": "$payments"},
            {
                "$group": {
                    "_id": "$payments.payment_type",
                    "payment_count": {"$sum": 1},
                    "total_amount": {"$sum": "$payments.payment_value"},
                    "average_amount": {"$avg": "$payments.payment_value"},
                }
            },
            {
                "$sort": {
                    "total_amount": -1,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "payment_type": "$_id",
                    "payment_count": 1,
                    "total_amount": {"$round": ["$total_amount", 2]},
                    "average_amount": {"$round": ["$average_amount", 2]},
                }
            },
        ]

        return list(self.collection.aggregate(pipeline))
