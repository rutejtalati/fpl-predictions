from typing import Any

import requests

from app.core.config import settings

API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"


class APIFootballClient:
    def __init__(self) -> None:
        self.api_key = (settings.apifootball_api_key or "").strip()

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise RuntimeError(
                "APIFOOTBALL_API_KEY is not set. Add it to backend environment variables."
            )
        return {
            "x-apisports-key": self.api_key,
            "Accept": "application/json",
        }

    def get_teams(self, league_id: int, season: int) -> dict[str, Any]:
        url = f"{API_FOOTBALL_BASE_URL}/teams"
        response = requests.get(
            url,
            headers=self._headers(),
            params={"league": league_id, "season": season},
            timeout=20,
        )
        response.raise_for_status()
        return response.json() if response.content else {}
