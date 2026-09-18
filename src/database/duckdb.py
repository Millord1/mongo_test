from pathlib import Path

import duckdb

from src.config.sql import QueryNames


class DuckDB:
    """Client DuckDB pour exécuter les requêtes SQL du projet."""

    def __init__(self, sql_dir: Path):
        self.connection = duckdb.connect()
        self.sql_dir = sql_dir

    def read_query(self, name: QueryNames) -> str:
        """Lit une requête SQL depuis le dossier sql/."""
        path = self.sql_dir / f"{name}.sql"

        if not path.exists():
            raise FileNotFoundError(f"Requête SQL introuvable : {path}")

        return path.read_text(encoding="utf-8")

    def query(self, name: QueryNames, **params):
        """Exécute une requête SQL avec ses paramètres."""
        sql = self.read_query(name)

        for key, value in params.items():
            sql = sql.replace(
                f"{{{{{key}}}}}",
                str(value),
            )

        return self.connection.sql(sql)

    @staticmethod
    def records(query) -> list[dict]:
        """Convertit un résultat DuckDB en liste de dictionnaires."""
        rows = query.fetchall()
        columns = [column[0] for column in query.description]

        return [dict(zip(columns, row, strict=False)) for row in rows]

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
