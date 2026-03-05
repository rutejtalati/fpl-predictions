from typing import Any

import requests

FPL_BOOTSTRAP_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"


def fetch_bootstrap_data(timeout: int = 25) -> dict[str, Any]:
    response = requests.get(FPL_BOOTSTRAP_URL, timeout=timeout)
    response.raise_for_status()
    return response.json()
