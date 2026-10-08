import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

from db import get_connection

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")

REPOS = [
    "dbt-labs/dbt-core",
    "apache/airflow",
    "apache/spark",
    "dagster-io/dagster",
    "PrefectHQ/prefect",
    "delta-io/delta",
    "apache/iceberg",
    "duckdb/duckdb",
]

API_URL = "https://api.github.com/repos/{repo}"

DDL = """
create table if not exists raw.repo_snapshots (
    repo_full_name text not null,
    snapshot_date  date not null,
    payload        jsonb not null,
    _ingested_at   timestamptz not null default now(),
    primary key (repo_full_name, snapshot_date)
)
"""

# Upsert: re-running on the same day overwrites instead of duplicating (idempotent)
UPSERT = """
insert into raw.repo_snapshots (repo_full_name, snapshot_date, payload)
values (%s, %s, %s)
on conflict (repo_full_name, snapshot_date)
do update set payload = excluded.payload, _ingested_at = now()
"""


def fetch_repo(repo):
    """Fetch repository metadata from the GitHub REST API."""
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
    }
    response = requests.get(API_URL.format(repo=repo), headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    # Use the UTC date so the snapshot key does not depend on the local timezone
    snapshot_date = datetime.now(timezone.utc).date()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
            for repo in REPOS:
                payload = fetch_repo(repo)
                cur.execute(UPSERT, (repo, snapshot_date, Jsonb(payload)))
                print(f"{repo}: stars={payload['stargazers_count']}")


if __name__ == "__main__":
    main()
