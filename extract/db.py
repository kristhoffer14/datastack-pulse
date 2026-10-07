import os

import psycopg
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("SUPABASE_DB_URL")

# Medallion-style layers: raw (as ingested) -> staging (cleaned) -> marts (analytics-ready)
SCHEMAS = ["raw", "staging", "marts"]


def get_connection():
    """Open a connection to Supabase. Reused by the extractor to avoid duplicated code."""
    return psycopg.connect(DB_URL)


if __name__ == "__main__":
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select version()")
            print("Connected:", cur.fetchone()[0])

            # Idempotent: safe to run multiple times
            for schema in SCHEMAS:
                cur.execute(f"create schema if not exists {schema}")

            # Parameterized query (%s) prevents SQL injection
            cur.execute(
                "select schema_name from information_schema.schemata "
                "where schema_name = any(%s) order by 1",
                (SCHEMAS,),
            )
            print("Schemas:", [row[0] for row in cur.fetchall()])