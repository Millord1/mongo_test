from datetime import datetime
from pathlib import Path

import duckdb
from dotenv import load_dotenv

from src.config.apis import DatasetNames
from src.database.mongodb import MongoDB

project_root = Path(__file__).resolve().parents[2]
data_dir = project_root / "data"
load_dotenv(project_root / ".env")

con = duckdb.connect()


def read_csv(dataset: str):
    path = data_dir / dataset
    return con.sql(f"SELECT * FROM read_csv_auto('{path.as_posix()}')")


def fetch_records(query) -> list[dict]:
    """Convertit directement le résultat DuckDB en dictionnaires Python."""
    rows = query.fetchall()
    columns = [column[0] for column in query.description]
    return [dict(zip(columns, row, strict=False)) for row in rows]


def clean_records(records: list[dict]) -> list[dict]:
    """Nettoie les None et s'assure que les objets datetime sont au bon format BSON."""
    cleaned = []
    for record in records:
        rec_copy = record.copy()
        for key, value in rec_copy.items():
            if value is None:
                rec_copy[key] = None
            elif isinstance(value, str) and (
                "_date" in key or "_timestamp" in key or "_at" in key
            ):
                try:
                    rec_copy[key] = datetime.fromisoformat(value)
                except ValueError:
                    pass
        cleaned.append(rec_copy)
    return cleaned


def import_all_collections():
    """Charge les CSV via DuckDB, assemble les documents et insère dans MongoDB."""
    print("🚀 Début du nettoyage et de l'importation...")

    with MongoDB() as db:
        print("- Import de la collection 'customers'...")
        customers = fetch_records(read_csv(DatasetNames.customers))
        db.customers.delete_many({})
        db.customers.insert_many(clean_records(customers))

        print("- Import de la collection 'sellers'...")
        sellers = fetch_records(read_csv(DatasetNames.sellers))
        db.sellers.delete_many({})
        db.sellers.insert_many(clean_records(sellers))

        print("- Import de la collection 'products'...")
        products_path = (data_dir / DatasetNames.products).as_posix()
        translations_path = (data_dir / DatasetNames.category_translation).as_posix()

        products_query = con.sql(
            f"""
            SELECT
                p.*,
                t.product_category_name_english
            FROM read_csv_auto('{products_path}') AS p
            LEFT JOIN read_csv(
                '{translations_path}',
                header = true,
                columns = {{
                    'product_category_name': 'VARCHAR',
                    'product_category_name_english': 'VARCHAR'
                }}
            ) AS t
                ON p.product_category_name = t.product_category_name
            """
        )

        products = fetch_records(products_query)
        db.products.delete_many({})
        db.products.insert_many(clean_records(products))

        print("- Traitement et assemblage des données pour 'orders'...")

        orders_path = (data_dir / DatasetNames.orders).as_posix()
        items_path = (data_dir / DatasetNames.order_items).as_posix()
        payments_path = (data_dir / DatasetNames.order_payments).as_posix()
        reviews_path = (data_dir / DatasetNames.order_reviews).as_posix()

        orders = con.sql(
            f"""
            SELECT
                * EXCLUDE (
                    order_purchase_timestamp,
                    order_approved_at,
                    order_delivered_carrier_date,
                    order_delivered_customer_date,
                    order_estimated_delivery_date
                ),
                CAST(order_purchase_timestamp AS TIMESTAMP) AS order_purchase_timestamp,
                CAST(order_approved_at AS TIMESTAMP) AS order_approved_at,
                CAST(
                        order_delivered_carrier_date AS TIMESTAMP
                    ) AS order_delivered_carrier_date,
                CAST(
                    order_delivered_customer_date AS TIMESTAMP
                ) AS order_delivered_customer_date,
                CAST(
                    order_estimated_delivery_date AS TIMESTAMP
                ) AS order_estimated_delivery_date
            FROM read_csv_auto('{orders_path}')
            """
        )

        items = con.sql(f"SELECT * FROM read_csv_auto('{items_path}')")
        payments = con.sql(f"SELECT * FROM read_csv_auto('{payments_path}')")
        reviews = con.sql(
            f"""
            SELECT
                * EXCLUDE (
                    review_creation_date,
                    review_answer_timestamp
                ),
                CAST(review_creation_date AS TIMESTAMP) AS review_creation_date,
                CAST(review_answer_timestamp AS TIMESTAMP) AS review_answer_timestamp
            FROM read_csv_auto('{reviews_path}')
            """
        )

        print("- Regroupement des items, paiements et avis...")

        orders_records = fetch_records(orders)
        items_records = fetch_records(items)
        payments_records = fetch_records(payments)
        reviews_records = fetch_records(reviews)

        items_by_order = {}
        for item in items_records:
            item_data = item.copy()
            order_id = item_data.pop("order_id")
            items_by_order.setdefault(order_id, []).append(item_data)

        payments_by_order = {}
        for payment in payments_records:
            payment_data = payment.copy()
            order_id = payment_data.pop("order_id")
            payments_by_order.setdefault(order_id, []).append(payment_data)

        reviews_by_order = {}
        for review in reviews_records:
            review_data = review.copy()
            order_id = review_data.pop("order_id")
            reviews_by_order.setdefault(order_id, []).append(review_data)

        print("- Assemblage des documents finalisé...")

        final_orders = []
        for order in orders_records:
            order_doc = order.copy()
            order_id = order_doc.pop("order_id")

            order_doc["_id"] = order_id
            order_doc["items"] = items_by_order.get(order_id, [])
            order_doc["payments"] = payments_by_order.get(order_id, [])
            order_doc["reviews"] = reviews_by_order.get(order_id, [])

            final_orders.append(order_doc)

        print("- Insertion dans MongoDB (collection 'orders')...")

        db.orders.delete_many({})
        db.orders.insert_many(clean_records(final_orders))

    print("✅ Import terminé avec succès !")


if __name__ == "__main__":
    import_all_collections()
