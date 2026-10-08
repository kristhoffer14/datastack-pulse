import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()  # Load variables from the .env file
TOKEN = os.getenv("GITHUB_TOKEN")


def get_rate_limit(token=None):
    """Return the GitHub API core rate limit, with or without authentication."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=30)
    response.raise_for_status()  # Raise an exception on HTTP errors (401, 403, ...)
    return response.json()["resources"]["core"]


if __name__ == "__main__":
    for label, tk in [("unauthenticated", None), ("authenticated", TOKEN)]:
        rate = get_rate_limit(tk)
        print(f"{label}: limit={rate['limit']}, remaining={rate['remaining']}")
        # 'reset' is a Unix timestamp (seconds since 1970-01-01 UTC)
        reset_time = datetime.fromtimestamp(rate["reset"], tz=timezone.utc)
        print(f"  resets at {reset_time.strftime('%Y-%m-%d %H:%M')} UTC")
