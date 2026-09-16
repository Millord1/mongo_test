from datetime import date, datetime
from typing import Any

from src.repositories.base_repository import BaseRepository

_NORMALIZATION = {
    "monthly_metrics": {
        "count_fields": (
            "orders",
            "delivered_orders",
            "cancelled_orders",
        ),
        "money_fields": (
            "revenue",
            "freight",
        ),
        "nullable_fields": (
            "avg_order_value",
            "avg_delivery_days",
            "avg_review_score",
        ),
        "count_field": "orders",
        "datetime_fields": (),
    },
    "product_analytics": {
        "count_fields": (
            "total_orders",
            "units_sold",
            "unique_sellers",
        ),
        "money_fields": (
            "revenue",
            "freight_revenue",
        ),
        "nullable_fields": ("avg_price",),
        "count_field": "total_orders",
        "datetime_fields": (),
    },
    "category_analytics": {
        "count_fields": (
            "orders",
            "units_sold",
        ),
        "money_fields": (
            "revenue",
            "freight_revenue",
        ),
        "nullable_fields": ("avg_price",),
        "id_fallback": "uncategorized",
        "count_field": "orders",
        "datetime_fields": (),
    },
    "seller_analytics": {
        "count_fields": (
            "orders",
            "delivered_orders",
        ),
        "money_fields": (
            "revenue",
            "freight_revenue",
        ),
        "nullable_fields": (
            "avg_order_value",
            "avg_delivery_days",
        ),
        "count_field": "orders",
        "datetime_fields": (),
    },
    "customer_analytics": {
        "count_fields": ("orders",),
        "money_fields": ("total_spent",),
        "nullable_fields": ("avg_order_value",),
        "count_field": "orders",
        "datetime_fields": (
            "first_order",
            "last_order",
        ),
    },
    "geography_analytics": {
        "count_fields": (
            "unique_customers",
            "orders",
        ),
        "money_fields": ("revenue",),
        "nullable_fields": ("avg_delivery_days",),
        "count_field": "orders",
        "datetime_fields": (),
    },
}


class AnalyticsRepository(BaseRepository):
    collection_name = "monthly_metrics"

    def get_monthly_metrics(self) -> list[dict]:
        return self._get_sorted_documents("monthly_metrics")

    def get_product_analytics(self) -> list[dict]:
        return self._get_sorted_documents("product_analytics")

    def get_category_analytics(self) -> list[dict]:
        return self._get_sorted_documents("category_analytics")

    def get_seller_analytics(self) -> list[dict]:
        return self._get_sorted_documents("seller_analytics")

    def get_customer_analytics(self) -> list[dict]:
        return self._get_sorted_documents("customer_analytics")

    def get_geography_analytics(self) -> list[dict]:
        return self._get_sorted_documents("geography_analytics")

    def _get_sorted_documents(self, collection_name: str) -> list[dict]:
        collection = getattr(self.db, collection_name, None)
        if collection is None:
            collection = self.db[collection_name]

        cursor = collection.find()
        sort = getattr(cursor, "sort", None)
        if sort is not None and not isinstance(cursor, list):
            try:
                sorted_cursor = sort("_id", 1)
            except TypeError:
                sorted_cursor = None
            if sorted_cursor is not None:
                cursor = sorted_cursor

        return self._normalize_documents(
            list(cursor),
            _NORMALIZATION[collection_name],
        )

    @classmethod
    def _normalize_documents(
        cls,
        documents: list[dict],
        normalization: dict[str, tuple | str],
    ) -> list[dict]:
        normalized_documents = []

        for document in documents:
            normalized = dict(document)
            if normalized.get("_id") is None:
                id_fallback = normalization.get("id_fallback")
                if id_fallback:
                    normalized["_id"] = id_fallback
            count_fields = normalization["count_fields"]
            money_fields = normalization["money_fields"]
            nullable_fields = normalization["nullable_fields"]
            datetime_fields = normalization["datetime_fields"]

            for field in count_fields:
                normalized[field] = cls._coerce_count(normalized.get(field))

            for field in money_fields:
                normalized[field] = cls._coerce_money(normalized.get(field))

            for field in nullable_fields:
                normalized[field] = cls._coerce_float(normalized.get(field))

            for field in datetime_fields:
                normalized[field] = cls._coerce_datetime(normalized.get(field))

            count_field = normalization["count_field"]
            if normalized[count_field] == 0:
                for field in count_fields:
                    normalized[field] = 0
                for field in money_fields:
                    normalized[field] = 0.0
                for field in nullable_fields:
                    normalized[field] = None

            normalized_documents.append(normalized)

        try:
            return sorted(
                normalized_documents,
                key=lambda document: document.get("_id", ""),
            )
        except TypeError:
            return sorted(
                normalized_documents,
                key=lambda document: str(document.get("_id", "")),
            )

    @staticmethod
    def _coerce_count(value: Any) -> int:
        if value is None:
            return 0

        try:
            if hasattr(value, "to_decimal"):
                value = value.to_decimal()
            if isinstance(value, str):
                value = value.strip()
            return int(value)
        except (TypeError, ValueError, OverflowError):
            return 0

    @staticmethod
    def _coerce_float(value: Any) -> float | None:
        if value is None:
            return None

        try:
            if hasattr(value, "to_decimal"):
                value = value.to_decimal()
            if isinstance(value, str) and not value.strip():
                return None
            result = float(value)
        except (TypeError, ValueError, OverflowError):
            return None

        if result != result or result in (float("inf"), float("-inf")):
            return None
        return result

    @staticmethod
    def _coerce_money(value: Any) -> float:
        result = AnalyticsRepository._coerce_float(value)
        return 0.0 if result is None else result

    @staticmethod
    def _coerce_datetime(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        if isinstance(value, str):
            normalized = value.strip()
            if normalized.endswith("Z"):
                normalized = f"{normalized[:-1]}+00:00"
            try:
                return datetime.fromisoformat(normalized)
            except ValueError:
                return None

        for method_name in ("as_datetime", "asDatetime"):
            method = getattr(value, method_name, None)
            if callable(method):
                try:
                    converted = method()
                    if isinstance(converted, datetime):
                        return converted
                except (TypeError, ValueError, OverflowError):
                    pass

        return None
