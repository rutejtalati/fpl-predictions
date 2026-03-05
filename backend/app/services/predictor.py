from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def _position_from_element_type(element_type: int) -> str:
    mapping = {
        1: "GK",
        2: "DEF",
        3: "MID",
        4: "FWD",
    }
    return mapping.get(element_type, "UNK")


def _build_team_lookup(teams: list[dict[str, Any]]) -> dict[int, str]:
    out: dict[int, str] = {}
    for row in teams:
        team_id = _to_int(row.get("id"), 0)
        if team_id <= 0:
            continue
        out[team_id] = str(row.get("short_name") or row.get("name") or "")
    return out


def _player_name(player: dict[str, Any]) -> str:
    first_name = str(player.get("first_name") or "").strip()
    second_name = str(player.get("second_name") or "").strip()
    return f"{first_name} {second_name}".strip()


def _predict_points(points_per_game: float, form: float, chance_playing: int, price: float) -> float:
    predicted = (points_per_game * 0.6) + (form * 0.4)
    predicted = predicted * (chance_playing / 100.0)
    predicted = predicted + max(0.0, (price - 4.0)) * 0.15
    return round(predicted, 2)


def build_player_predictions(bootstrap: dict[str, Any]) -> list[dict[str, Any]]:
    players = bootstrap.get("elements", []) or []
    teams = bootstrap.get("teams", []) or []
    team_lookup = _build_team_lookup(teams)

    out: list[dict[str, Any]] = []
    for player in players:
        player_id = _to_int(player.get("id"), 0)
        if player_id <= 0:
            continue

        team_id = _to_int(player.get("team"), 0)
        team_name = team_lookup.get(team_id, "")

        element_type = _to_int(player.get("element_type"), 0)
        position = _position_from_element_type(element_type)

        price = round(_to_float(player.get("now_cost"), 0.0) / 10.0, 1)
        form = _to_float(player.get("form"), 0.0)
        points_per_game = _to_float(player.get("points_per_game"), 0.0)

        chance_raw = player.get("chance_of_playing_next_round")
        chance_playing = 100 if chance_raw is None else _to_int(chance_raw, 100)
        chance_playing = max(0, min(100, chance_playing))

        predicted_points = _predict_points(
            points_per_game=points_per_game,
            form=form,
            chance_playing=chance_playing,
            price=price,
        )

        out.append(
            {
                "id": player_id,
                "name": _player_name(player),
                "team": team_name,
                "team_id": team_id,
                "position": position,
                "price": price,
                "predicted_points": predicted_points,
                "chance_playing": chance_playing,
                "form": round(form, 2),
                "points_per_game": round(points_per_game, 2),
            }
        )

    out.sort(key=lambda row: row["predicted_points"], reverse=True)
    return out


def filter_predictions(
    predictions: list[dict[str, Any]],
    search: str | None,
    team_id: int | None,
    position: str | None,
    min_price: float | None,
    max_price: float | None,
    limit: int,
) -> list[dict[str, Any]]:
    rows = predictions

    if search:
        query = search.strip().lower()
        rows = [row for row in rows if query in row["name"].lower()]

    if team_id is not None:
        rows = [row for row in rows if int(row.get("team_id", 0)) == int(team_id)]

    if position:
        pos = position.strip().upper()
        rows = [row for row in rows if str(row.get("position", "")).upper() == pos]

    if min_price is not None:
        rows = [row for row in rows if float(row.get("price", 0.0)) >= float(min_price)]

    if max_price is not None:
        rows = [row for row in rows if float(row.get("price", 0.0)) <= float(max_price)]

    if limit > 0:
        rows = rows[:limit]

    return rows
