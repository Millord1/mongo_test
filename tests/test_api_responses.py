from datetime import datetime
from unittest import TestCase, skipIf

from fastapi import FastAPI
from pymongo.errors import PyMongoError

from src.main import mongo_exception_handler

try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None

from src.api.routers import analytics, customers, orders, products
from src.repositories.analytics_repository import _NORMALIZATION, AnalyticsRepository
from src.schemas.analytics import (
    CategoryAnalyticsResponse,
    CustomerAnalyticsResponse,
    GeographyAnalyticsResponse,
    MonthlyMetricsResponse,
    ProductAnalyticsResponse,
    SellerAnalyticsResponse,
)


class AnalyticsResponseModelTests(TestCase):
    def test_mongo_id_aliases_are_serialized_as_mongo_ids(self):
        cases = [
            (
                MonthlyMetricsResponse,
                {
                    "_id": datetime(2026, 1, 1),
                    "orders": 1,
                    "delivered_orders": 1,
                    "cancelled_orders": 0,
                    "revenue": 12.0,
                    "freight": 2.0,
                    "avg_order_value": 12.0,
                },
            ),
            (
                ProductAnalyticsResponse,
                {
                    "_id": "product-1",
                    "product_category_name": "bed_bath_table",
                    "product_category_name_english": "bed_bath_table",
                    "total_orders": 1,
                    "units_sold": 1,
                    "revenue": 12.0,
                    "freight_revenue": 2.0,
                    "avg_price": 10.0,
                    "unique_sellers": 1,
                },
            ),
            (
                CategoryAnalyticsResponse,
                {
                    "_id": "category-1",
                    "category_english": "Category",
                    "orders": 1,
                    "units_sold": 1,
                    "revenue": 12.0,
                    "freight_revenue": 2.0,
                    "avg_price": 10.0,
                },
            ),
            (
                SellerAnalyticsResponse,
                {
                    "_id": "seller-1",
                    "orders": 1,
                    "revenue": 12.0,
                    "freight_revenue": 2.0,
                    "avg_order_value": 12.0,
                    "avg_delivery_days": 3.0,
                    "delivered_orders": 1,
                },
            ),
            (
                CustomerAnalyticsResponse,
                {
                    "_id": "customer-1",
                    "customer_unique_id": "unique-1",
                    "customer_zip_code_prefix": 1000,
                    "customer_city": "City",
                    "customer_state": "SP",
                    "orders": 1,
                    "total_spent": 12.0,
                    "avg_order_value": 12.0,
                    "first_order": datetime(2026, 1, 1),
                    "last_order": datetime(2026, 1, 2),
                },
            ),
            (
                GeographyAnalyticsResponse,
                {
                    "_id": "SP",
                    "unique_customers": 1,
                    "orders": 1,
                    "revenue": 12.0,
                    "avg_delivery_days": 3.0,
                },
            ),
        ]

        for model, document in cases:
            with self.subTest(model=model.__name__):
                validated = model.model_validate(document)
                self.assertEqual(
                    validated.model_dump(by_alias=True)["_id"],
                    document["_id"],
                )

    def test_no_sale_values_use_zero_counts_and_null_averages(self):
        product = ProductAnalyticsResponse.model_validate(
            {
                "_id": "product-1",
                "total_orders": 0,
                "units_sold": 0,
                "revenue": 0.0,
                "freight_revenue": 0.0,
                "avg_price": None,
                "unique_sellers": 0,
            }
        )
        customer = CustomerAnalyticsResponse.model_validate(
            {
                "_id": "customer-1",
                "customer_unique_id": "unique-1",
                "customer_zip_code_prefix": 1000,
                "customer_city": "City",
                "customer_state": "SP",
                "orders": 0,
                "total_spent": 0.0,
                "avg_order_value": None,
                "first_order": None,
                "last_order": None,
            }
        )

        self.assertEqual(product.units_sold, 0)
        self.assertEqual(product.revenue, 0.0)
        self.assertIsNone(product.avg_price)
        self.assertEqual(customer.orders, 0)
        self.assertEqual(customer.total_spent, 0.0)
        self.assertIsNone(customer.avg_order_value)


class AnalyticsRepositoryNormalizationTests(TestCase):
    def test_repository_normalizes_missing_aggregates(self):
        documents = AnalyticsRepository._normalize_documents(
            [
                {
                    "_id": "product-1",
                    "total_orders": None,
                    "units_sold": None,
                    "revenue": None,
                    "freight_revenue": None,
                    "avg_price": None,
                    "unique_sellers": None,
                }
            ],
            _NORMALIZATION["product_analytics"],
        )

        self.assertEqual(
            documents[0],
            {
                "_id": "product-1",
                "total_orders": 0,
                "units_sold": 0,
                "revenue": 0.0,
                "freight_revenue": 0.0,
                "avg_price": None,
                "unique_sellers": 0,
            },
        )

    def test_null_category_id_uses_sql_fallback(self):
        documents = AnalyticsRepository._normalize_documents(
            [{"_id": None, "orders": 0, "units_sold": 0, "revenue": None}],
            _NORMALIZATION["category_analytics"],
        )

        self.assertEqual(documents[0]["_id"], "uncategorized")


@skipIf(TestClient is None, "httpx is required for TestClient")
class ApiRouteContractTests(TestCase):
    def test_analytics_endpoint_returns_mongo_id(self):
        class FakeAnalyticsRepository:
            def get_product_analytics(self, limit=20):
                return [
                    {
                        "_id": "product-1",
                        "product_category_name": None,
                        "product_category_name_english": None,
                        "total_orders": 0,
                        "units_sold": 0,
                        "revenue": 0.0,
                        "freight_revenue": 0.0,
                        "avg_price": None,
                        "unique_sellers": 0,
                    }
                ]

        app = FastAPI()
        app.include_router(analytics.router)
        app.dependency_overrides[analytics.get_analytics_repository] = (
            lambda: FakeAnalyticsRepository()
        )

        with TestClient(app) as client:
            response = client.get("/analytics/products")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["_id"], "product-1")
        self.assertNotIn("product_id", response.json()[0])

    def test_product_pagination_rejects_zero_size(self):
        class FakeProductRepository:
            def get_all_offset(self, skip, limit):
                return [], 0

        app = FastAPI()
        app.include_router(products.router)
        app.dependency_overrides[products.get_product_repository] = (
            lambda: FakeProductRepository()
        )

        with TestClient(app) as client:
            response = client.get("/products?size=0")

        self.assertEqual(response.status_code, 422)

    def test_order_endpoint_uses_typed_mongo_id_contract(self):
        class FakeOrderRepository:
            def get_all_offset(self, skip, limit, filters=None):
                return [
                    {
                        "_id": "order-1",
                        "customer_id": "customer-1",
                        "order_status": "delivered",
                        "items": [],
                        "payments": [],
                        "reviews": [],
                    }
                ], 1

        app = FastAPI()
        app.include_router(orders.router)
        app.dependency_overrides[orders.get_order_repository] = (
            lambda: FakeOrderRepository()
        )

        with TestClient(app) as client:
            response = client.get("/orders")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"][0]["_id"], "order-1")
        self.assertNotIn("id", response.json()["items"][0])

    def test_customer_endpoint_serializes_mongo_id(self):
        class FakeCustomerRepository:
            def get_all_offset(self, skip, limit):
                return [
                    {
                        "_id": "customer-1",
                        "customer_unique_id": "unique-1",
                        "customer_zip_code_prefix": 1000,
                        "customer_city": "City",
                        "customer_state": "SP",
                    }
                ], 1

        app = FastAPI()
        app.include_router(customers.router)
        app.dependency_overrides[customers.get_customer_repository] = (
            lambda: FakeCustomerRepository()
        )

        with TestClient(app) as client:
            response = client.get("/customers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"][0]["_id"], "customer-1")
        self.assertNotIn("customer_id", response.json()["items"][0])

    def test_analytics_limit_rejects_value_above_100(self):
        class FakeAnalyticsRepository:
            def get_product_analytics(self, limit=20):
                return []

        app = FastAPI()
        app.include_router(analytics.router)
        app.dependency_overrides[analytics.get_analytics_repository] = (
            lambda: FakeAnalyticsRepository()
        )

        with TestClient(app) as client:
            response = client.get("/analytics/products?limit=500")

        self.assertEqual(response.status_code, 422)

    def test_missing_order_returns_404(self):
        class FakeOrderRepository:
            def get_by_id(self, order_id):
                return None

        app = FastAPI()
        app.include_router(orders.router)
        app.dependency_overrides[orders.get_order_repository] = (
            lambda: FakeOrderRepository()
        )

        with TestClient(app) as client:
            response = client.get("/orders/order-does-not-exist")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["detail"],
            "Commande introuvable",
        )

    def test_mongodb_error_returns_503(self):
        app = FastAPI()
        app.add_exception_handler(
            PyMongoError,
            mongo_exception_handler,
        )

        @app.get("/mongo-error")
        def mongo_error():
            raise PyMongoError("MongoDB unavailable")

        with TestClient(app) as client:
            response = client.get("/mongo-error")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["detail"],
            "Service MongoDB temporairement indisponible",
        )
