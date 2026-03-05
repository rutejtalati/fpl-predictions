from fastapi import APIRouter

from app.services.fpl_client import fetch_bootstrap_data

router = APIRouter(prefix="/fpl", tags=["fpl"])


@router.get("/bootstrap")
def get_fpl_bootstrap() -> dict:
    payload = fetch_bootstrap_data()
    players = payload.get("elements", []) or []
    teams = payload.get("teams", []) or []

    slim_players = []
    for player in players:
        slim_players.append(
            {
                "id": player.get("id"),
                "first_name": player.get("first_name"),
                "second_name": player.get("second_name"),
                "team": player.get("team"),
                "element_type": player.get("element_type"),
                "now_cost": player.get("now_cost"),
                "form": player.get("form"),
                "points_per_game": player.get("points_per_game"),
                "chance_of_playing_next_round": player.get("chance_of_playing_next_round"),
            }
        )

    slim_teams = []
    for team in teams:
        slim_teams.append(
            {
                "id": team.get("id"),
                "name": team.get("name"),
                "short_name": team.get("short_name"),
            }
        )

    return {
        "players": slim_players,
        "teams": slim_teams,
        "total_players": len(slim_players),
    }
