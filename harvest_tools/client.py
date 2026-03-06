import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BASE_URL = "https://api.harvestapp.com/v2"


def get_client() -> httpx.Client:
    token = os.environ["HARVEST_ACCESS_TOKEN"]
    account_id = os.environ["HARVEST_ACCOUNT_ID"]
    return httpx.Client(
        base_url=BASE_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Harvest-Account-Id": account_id,
            "User-Agent": "harvest-tools",
        },
    )
