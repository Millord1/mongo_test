from pathlib import Path

import duckdb

from src.config.apis import DatasetNames

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
REPORT = ROOT / "reports" / "data_quality_report.md"


def source(dataset: DatasetNames) -> str:
    path = (DATA / dataset.value).as_posix().replace("'", "''")
    return f"read_csv_auto('{path}', header=true)"


def ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def scalar(db, sql: str) -> int:
    return int(db.execute(sql).fetchone()[0] or 0)


def column_types(
    db,
    dataset: DatasetNames,
) -> list[tuple[str, str]]:
    rows = db.execute(
        f"""
        DESCRIBE
        SELECT *
        FROM {source(dataset)}
        """
    ).fetchall()

    return [(column_name, column_type) for column_name, column_type, *_ in rows]


def duplicate_count(
    db,
    dataset: DatasetNames,
    keys: tuple[str, ...],
) -> int:
    columns = ", ".join(ident(key) for key in keys)

    return scalar(
        db,
        f"""
        SELECT COALESCE(SUM(n - 1), 0)
        FROM (
            SELECT {columns}, COUNT(*) AS n
            FROM {source(dataset)}
            GROUP BY {columns}
            HAVING COUNT(*) > 1
        ) duplicates
        """,
    )


def orphan_count(
    db,
    child: DatasetNames,
    parent: DatasetNames,
    child_key: str,
    parent_key: str,
) -> int:
    child_column = ident(child_key)
    parent_column = ident(parent_key)

    return scalar(
        db,
        f"""
        SELECT COUNT(*)
        FROM {source(child)} AS child
        LEFT JOIN {source(parent)} AS parent
            ON child.{child_column} = parent.{parent_column}
        WHERE child.{child_column} IS NOT NULL
            AND parent.{parent_column} IS NULL
        """,
    )


def main() -> None:
    missing_files = [
        dataset.value for dataset in DatasetNames if not (DATA / dataset.value).exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Fichiers absents de data/: " + ", ".join(missing_files)
        )

    db = duckdb.connect()

    lines = [
        "# Rapport de qualité des données Olist",
        "",
        "## 1. Fichiers retenus",
        "",
        "| Fichier | Lignes |",
        "|---|---:|",
    ]

    row_counts = {}

    for dataset in DatasetNames:
        count = scalar(
            db,
            f"SELECT COUNT(*) FROM {source(dataset)}",
        )

        row_counts[dataset] = count

        lines.append(f"| `{dataset.value}` | {count:,} |")

    lines += [
        "",
        "## 2. Types des colonnes",
        "",
        (
            "Les types ci-dessous sont inférés automatiquement "
            "par DuckDB à partir des fichiers CSV."
        ),
        "",
    ]

    for dataset in DatasetNames:
        lines += [
            f"### {dataset.value}",
            "",
            "| Colonne | Type inféré |",
            "|---|---|",
        ]

        for column_name, column_type in column_types(
            db,
            dataset,
        ):
            lines.append(f"| `{column_name}` | `{column_type}` |")

        lines.append("")

    lines += [
        "",
        "## 3. Valeurs manquantes",
        "",
    ]

    for dataset in DatasetNames:
        cursor = db.execute(f"SELECT * FROM {source(dataset)} LIMIT 0")

        columns = [column[0] for column in cursor.description]

        expressions = [
            (
                "SUM(CASE WHEN "
                f"{ident(column)} IS NULL "
                f"OR TRIM(CAST({ident(column)} AS VARCHAR)) = '' "
                "THEN 1 ELSE 0 END)"
            )
            for column in columns
        ]

        values = db.execute(
            f"""
            SELECT {", ".join(expressions)}
            FROM {source(dataset)}
            """
        ).fetchone()

        missing = [
            (column, count)
            for column, count in zip(
                columns,
                values,
                strict=False,
            )
            if count
        ]

        lines += [
            f"### {dataset.value}",
            "",
        ]

        if not missing:
            lines += [
                "Aucune valeur manquante détectée.",
                "",
            ]
            continue

        lines += [
            "| Colonne | Manquantes | % |",
            "|---|---:|---:|",
        ]

        for column, count in missing:
            percentage = count / row_counts[dataset] * 100

            lines.append(f"| `{column}` | " f"{count:,} | " f"{percentage:.2f}% |")

        lines.append("")

    duplicate_checks = [
        (
            DatasetNames.customers,
            ("customer_id",),
        ),
        (
            DatasetNames.sellers,
            ("seller_id",),
        ),
        (
            DatasetNames.products,
            ("product_id",),
        ),
        (
            DatasetNames.orders,
            ("order_id",),
        ),
        (
            DatasetNames.order_items,
            ("order_id", "order_item_id"),
        ),
        (
            DatasetNames.order_payments,
            ("order_id", "payment_sequential"),
        ),
    ]

    lines += [
        "## 4. Doublons sur les clés",
        "",
        "| Fichier | Clé | Doublons supplémentaires |",
        "|---|---|---:|",
    ]

    for dataset, keys in duplicate_checks:
        count = duplicate_count(
            db,
            dataset,
            keys,
        )

        lines.append(
            f"| `{dataset.value}` | " f"`{' + '.join(keys)}` | " f"{count:,} |"
        )

    relation_checks = [
        (
            "Orders sans customer",
            DatasetNames.orders,
            DatasetNames.customers,
            "customer_id",
            "customer_id",
        ),
        (
            "Items sans order",
            DatasetNames.order_items,
            DatasetNames.orders,
            "order_id",
            "order_id",
        ),
        (
            "Items sans product",
            DatasetNames.order_items,
            DatasetNames.products,
            "product_id",
            "product_id",
        ),
        (
            "Items sans seller",
            DatasetNames.order_items,
            DatasetNames.sellers,
            "seller_id",
            "seller_id",
        ),
        (
            "Payments sans order",
            DatasetNames.order_payments,
            DatasetNames.orders,
            "order_id",
            "order_id",
        ),
        (
            "Reviews sans order",
            DatasetNames.order_reviews,
            DatasetNames.orders,
            "order_id",
            "order_id",
        ),
    ]

    lines += [
        "",
        "## 5. Intégrité des relations",
        "",
        "| Contrôle | Lignes concernées |",
        "|---|---:|",
    ]

    for (
        label,
        child,
        parent,
        child_key,
        parent_key,
    ) in relation_checks:
        count = orphan_count(
            db,
            child,
            parent,
            child_key,
            parent_key,
        )

        lines.append(f"| {label} | {count:,} |")

    orders = source(DatasetNames.orders)

    date_checks = {
        "Approbation avant achat": (
            "order_approved_at",
            "order_purchase_timestamp",
        ),
        "Transporteur avant achat": (
            "order_delivered_carrier_date",
            "order_purchase_timestamp",
        ),
        "Livraison client avant achat": (
            "order_delivered_customer_date",
            "order_purchase_timestamp",
        ),
        "Livraison client avant transporteur": (
            "order_delivered_customer_date",
            "order_delivered_carrier_date",
        ),
        "Livraison estimée avant achat": (
            "order_estimated_delivery_date",
            "order_purchase_timestamp",
        ),
    }

    lines += [
        "",
        "## 6. Cohérence des dates",
        "",
        "| Contrôle | Lignes concernées |",
        "|---|---:|",
    ]

    for label, (
        later,
        earlier,
    ) in date_checks.items():
        count = scalar(
            db,
            f"""
            SELECT COUNT(*)
            FROM {orders}
            WHERE TRY_CAST(
                {ident(later)}
                AS TIMESTAMP
            ) IS NOT NULL
                AND TRY_CAST(
                {ident(earlier)}
                AS TIMESTAMP
            ) IS NOT NULL
                AND TRY_CAST(
                {ident(later)}
                AS TIMESTAMP
            )
                <
                TRY_CAST(
                {ident(earlier)}
                AS TIMESTAMP
            )
            """,
        )

        lines.append(f"| {label} | {count:,} |")

    lines += [
        "",
        "## 7. Conclusion",
        "",
        (
            "Ce rapport documente les volumes, "
            "types de colonnes, valeurs manquantes, "
            "doublons, relations entre fichiers et "
            "incohérences de dates avant "
            "l'import MongoDB."
        ),
        "",
    ]

    db.close()

    REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"Rapport généré : {REPORT}")


if __name__ == "__main__":
    main()
