import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "company.db"


def get_connection() -> sqlite3.Connection:
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DB_PATH)

    # Return rows that behave like dictionaries.
    connection.row_factory = sqlite3.Row

    return connection


def get_schema() -> str:
    """Return the database schema as readable text."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)

        tables = cursor.fetchall()

        schema_parts = []

        for table in tables:
            table_name = table["name"]

            cursor.execute(
                f"PRAGMA table_info({table_name})"
            )

            columns = cursor.fetchall()

            schema_parts.append(f"Table {table_name}:")

            for column in columns:
                schema_parts.append(
                    f"- {column['name']} {column['type']}"
                )

            schema_parts.append("")

        return "\n".join(schema_parts)

    finally:
        connection.close()


def execute_query(sql: str) -> list[dict]:
    """Execute a SQL query and return the results."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(sql)

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()