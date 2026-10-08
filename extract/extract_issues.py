import argparse
import time
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv
from psycopg.types.json import Jsonb
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from db import get_connection
from extract_repos import REPOS, TOKEN

load_dotenv()

API_URL = "https://api.github.com/repos/{repo}/issues"

DDL = """
create table if not exists raw.issues (
    repo_full_name text not null,
    issue_id       bigint not null,
    updated_at     timestamptz not null,
    payload        jsonb not null,
    _ingested_at   timestamptz not null default now(),
    primary key (repo_full_name, issue_id)
)
"""

# Upsert: a changed issue replaces its previous version (idempotent)
UPSERT = """
insert into raw.issues (repo_full_name, issue_id, updated_at, payload)
values (%s, %s, %s, %s)
on conflict (repo_full_name, issue_id)
do update set updated_at = excluded.updated_at,
              payload = excluded.payload,
              _ingested_at = now()
"""


def build_session():
    """Create an HTTP session with auth headers and automatic retries on 5xx errors."""
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update(
        {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
        }
    )
    return session


def get_watermark(cur, repo):
    """Return the latest updated_at already loaded for a repo (None on first run)."""
    cur.execute("select max(updated_at) from raw.issues where repo_full_name = %s", (repo,))
    return cur.fetchone()[0]


def fetch_issues(session, repo, since):
    """Yield every issue/PR updated since `since`, following API pagination."""
    url = API_URL.format(repo=repo)
    params = {
        "state": "all",
        "since": since.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": 100,
        "sort": "updated",
        "direction": "asc",  # oldest first, so the watermark never skips items
    }
    while url:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        yield from response.json()

        # The 'next' link already contains the full query string
        url = response.links.get("next", {}).get("url")
        params = None

        # Respect the rate limit: if exhausted, sleep until the window resets
        if int(response.headers.get("X-RateLimit-Remaining", 1)) == 0:
            reset = int(response.headers["X-RateLimit-Reset"])
            time.sleep(max(reset - time.time(), 0) + 1)


def main(since_days):
    default_since = datetime.now(timezone.utc) - timedelta(days=since_days)
    session = build_session()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
            conn.commit()

            for repo in REPOS:
                # Incremental: resume from the watermark; first run uses the window
                since = get_watermark(cur, repo) or default_since
                count = 0
                for issue in fetch_issues(session, repo, since):
                    cur.execute(
                        UPSERT,
                        (repo, issue["id"], issue["updated_at"], Jsonb(issue)),
                    )
                    count += 1
                conn.commit()  # commit per repo, so a failure keeps earlier repos
                print(f"{repo}: {count} items upserted (since {since:%Y-%m-%d %H:%M} UTC)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Incrementally load GitHub issues and PRs into raw.issues"
    )
    parser.add_argument(
        "--since-days",
        type=int,
        default=90,
        help="Lookback window for the first run (ignored once a watermark exists)",
    )
    args = parser.parse_args()
    main(args.since_days)
