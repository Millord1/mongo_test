from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv

from src.config.apis import DatasetNames
from src.config.sql import QueryNames
from src.database.duckdb import DuckDB
from src.database.mongodb import MongoDB

from src.ingestion.importer import ensure_csv_files_present

project_root = Path(__file__).resolve().parents[2]
data_dir = project_root / "data"
sql_dir = project_root / "src" / "sql"

load_dotenv(project_root / ".env", override=False)


def clean_records(records: list[dict]) -> list[dict]:
    """Convertit les dates en types compatibles avec BSON."""
    cleaned = []

    for record in records:
        cleaned_record = record.copy()

        for key, value in cleaned_record.items():
            if value is None:
                continue

            if isinstance(value, datetime):
                continue

            if isinstance(value, date):
                cleaned_record[key] = datetime.combine(
                    value,
                    datetime.min.time(),
                )
                continue

            if isinstance(value, str) and (
                "_date" in key or "_timestamp" in key or "_at" in key
            ):
                try:
                    cleaned_record[key] = datetime.fromisoformat(value)
                except ValueError:
                    pass

        cleaned.append(cleaned_record)

    return cleaned


def replace_collection(collection, records: list[dict]):
    """Remplace complètement le contenu d'une collection."""
    collection.delete_many({})

    if records:
        collection.insert_many(records)


def dataset_path(dataset: DatasetNames) -> str:
    return (data_dir / dataset).as_posix()


def import_query(
    duckdb: DuckDB,
    db,
    query: QueryNames,
    *,
    id_field: str | None = None,
    **params,
):
    print(f"- Import de la collection '{query.value}'...")

    records = duckdb.records(duckdb.query(query, **params))
    print(f"DEBUG {query.value}:")
    print(records[0] if records else "Aucun résultat")
    print(f"Colonnes: {list(records[0].keys()) if records else []}")
    if id_field:
        for record in records:
            record["_id"] = record.pop(id_field)

    replace_collection(
        getattr(db, query.value),
        clean_records(records),
    )

    print(f"  ✓ {len(records)} documents importés")


def create_orders_collection(duckdb: DuckDB, db):
    print("- Traitement et assemblage des données pour 'orders'...")

    orders = duckdb.records(
        duckdb.query(
            QueryNames.ORDERS,
            orders_path=dataset_path(DatasetNames.orders),
        )
    )

    items = duckdb.records(
        duckdb.query(
            QueryNames.ORDER_ITEMS,
            items_path=dataset_path(DatasetNames.order_items),
        )
    )

    payments = duckdb.records(
        duckdb.query(
            QueryNames.ORDER_PAYMENTS,
            payments_path=dataset_path(DatasetNames.order_payments),
        )
    )

    reviews = duckdb.records(
        duckdb.query(
            QueryNames.ORDER_REVIEWS,
            reviews_path=dataset_path(DatasetNames.order_reviews),
        )
    )

    print("- Regroupement des items, paiements et avis...")

    items_by_order = group_by_order(items)
    payments_by_order = group_by_order(payments)
    reviews_by_order = group_by_order(reviews)

    final_orders = []

    for order in orders:
        order_id = order.pop("order_id")

        order["_id"] = order_id
        order["items"] = items_by_order.get(order_id, [])
        order["payments"] = payments_by_order.get(order_id, [])
        order["reviews"] = reviews_by_order.get(order_id, [])

        final_orders.append(order)

    print("- Insertion dans MongoDB (collection 'orders')...")

    replace_collection(
        db.orders,
        clean_records(final_orders),
    )


def group_by_order(records: list[dict]) -> dict[str, list[dict]]:
    """Regroupe des documents par order_id."""
    grouped = {}

    for record in records:
        record = record.copy()
        order_id = record.pop("order_id")

        grouped.setdefault(order_id, []).append(record)

    return grouped


def import_all_collections():
    print("Nettoyage et importation")

    with DuckDB(sql_dir) as duckdb, MongoDB() as db:
        import_query(
            duckdb,
            db,
            QueryNames.CUSTOMERS,
            id_field="customer_id",
            customers_path=dataset_path(DatasetNames.customers),
        )

        import_query(
            duckdb,
            db,
            QueryNames.SELLERS,
            id_field="seller_id",
            sellers_path=dataset_path(DatasetNames.sellers),
        )

        import_query(
            duckdb,
            db,
            QueryNames.PRODUCTS,
            id_field="product_id",
            products_path=dataset_path(DatasetNames.products),
            translations_path=dataset_path(DatasetNames.category_translation),
        )

        create_orders_collection(duckdb, db)

        print("\nCréation des collections analytiques")

        import_query(
            duckdb,
            db,
            QueryNames.MONTHLY_METRICS,
            id_field="month",
            orders_path=dataset_path(DatasetNames.orders),
            items_path=dataset_path(DatasetNames.order_items),
            reviews_path=dataset_path(DatasetNames.order_reviews),
        )

        import_query(
            duckdb,
            db,
            QueryNames.PRODUCT_ANALYTICS,
            id_field="product_id",
            products_path=dataset_path(DatasetNames.products),
            items_path=dataset_path(DatasetNames.order_items),
            translations_path=dataset_path(DatasetNames.category_translation),
        )

        import_query(
            duckdb,
            db,
            QueryNames.CATEGORY_ANALYTICS,
            id_field="category",
            products_path=dataset_path(DatasetNames.products),
            items_path=dataset_path(DatasetNames.order_items),
            translations_path=dataset_path(DatasetNames.category_translation),
        )

        import_query(
            duckdb,
            db,
            QueryNames.SELLER_ANALYTICS,
            id_field="seller_id",
            sellers_path=dataset_path(DatasetNames.sellers),
            items_path=dataset_path(DatasetNames.order_items),
            orders_path=dataset_path(DatasetNames.orders),
        )

        import_query(
            duckdb,
            db,
            QueryNames.CUSTOMER_ANALYTICS,
            id_field="customer_id",
            customers_path=dataset_path(DatasetNames.customers),
            orders_path=dataset_path(DatasetNames.orders),
            items_path=dataset_path(DatasetNames.order_items),
        )

        import_query(
            duckdb,
            db,
            QueryNames.GEOGRAPHY_ANALYTICS,
            id_field="state",
            customers_path=dataset_path(DatasetNames.customers),
            orders_path=dataset_path(DatasetNames.orders),
            items_path=dataset_path(DatasetNames.order_items),
        )

    print("\n✅ Import terminé avec succès !")


def run_ingestion():
    """Vérifie les fichiers sources puis importe les données dans MongoDB."""
    ensure_csv_files_present()
    import_all_collections()


if __name__ == "__main__":
    run_ingestion()
