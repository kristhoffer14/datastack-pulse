import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()  # lee el archivo .env y carga sus variables
TOKEN = os.getenv("GITHUB_TOKEN")


def get_rate_limit(token=None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(
        "https://api.github.com/rate_limit", headers=headers, timeout=30
    )
    response.raise_for_status()  # si hay error HTTP (401, 403...), lanza excepción
    return response.json()["resources"]["core"]


if __name__ == "__main__":
    for label, tk in [("sin token", None), ("con token", TOKEN)]:
        rate = get_rate_limit(tk)
        print(f"{label}: límite={rate['limit']}, restantes={rate['remaining']}")
        reset_time = datetime.fromtimestamp(rate["reset"], tz=timezone.utc)
        print(f"  se reinicia a las {reset_time.strftime('%Y-%m-%d %H:%M')} UTC")