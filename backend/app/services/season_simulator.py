import random
from collections import defaultdict
from datetime import datetime

from app.services.match_simulator import simulate_match


def _percentile(sorted_values: list[int], percentile: float) -> int:
    if not sorted_values:
        return 0
    rank = int(round((len(sorted_values) - 1) * percentile))
    rank = max(0, min(len(sorted_values) - 1, rank))
    return int(sorted_values[rank])


def _most_common(values: list[int]) -> int:
    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    top_rank = 1
    top_count = -1
    for rank, count in counts.items():
        if count > top_count:
            top_rank = rank
            top_count = count
    return int(top_rank)


def _init_team_stats(team_strengths: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    stats: dict[str, dict[str, float]] = {}
    for team_name in team_strengths.keys():
        stats[team_name] = {
            "points": 0.0,
            "gf": 0.0,
            "ga": 0.0,
        }
    return stats


def _sorted_table(stats: dict[str, dict[str, float]]) -> list[tuple[str, dict[str, float]]]:
    rows = list(stats.items())
    rows.sort(
        key=lambda row: (
            row[1]["points"],
            row[1]["gf"] - row[1]["ga"],
            row[1]["gf"],
        ),
        reverse=True,
    )
    return rows


def _match_expected_goals(home_team: str, away_team: str, team_strengths: dict[str, dict[str, float]]) -> tuple[float, float]:
    home = team_strengths.get(home_team, {})
    away = team_strengths.get(away_team, {})

    home_attack = float(home.get("attack", 1.0))
    home_defense = float(home.get("defense", 1.0))
    home_form = float(home.get("recent_form", 0.0))

    away_attack = float(away.get("attack", 1.0))
    away_defense = float(away.get("defense", 1.0))
    away_form = float(away.get("recent_form", 0.0))

    home_xg = 1.25 + (home_attack - 1.0) * 0.70 - (away_defense - 1.0) * 0.55 + home_form * 0.10 + 0.20
    away_xg = 1.10 + (away_attack - 1.0) * 0.65 - (home_defense - 1.0) * 0.55 + away_form * 0.10

    home_xg = max(0.25, min(3.5, home_xg))
    away_xg = max(0.20, min(3.2, away_xg))
    return round(home_xg, 3), round(away_xg, 3)


def _apply_match_result(stats: dict[str, dict[str, float]], home_team: str, away_team: str, home_goals: int, away_goals: int) -> None:
    stats[home_team]["gf"] += home_goals
    stats[home_team]["ga"] += away_goals
    stats[away_team]["gf"] += away_goals
    stats[away_team]["ga"] += home_goals

    if home_goals > away_goals:
        stats[home_team]["points"] += 3
    elif home_goals < away_goals:
        stats[away_team]["points"] += 3
    else:
        stats[home_team]["points"] += 1
        stats[away_team]["points"] += 1


def _build_fixture_models(fixtures: list[dict], team_strengths: dict[str, dict[str, float]]) -> list[dict]:
    models: list[dict] = []
    for fixture in fixtures:
        home_team = str(fixture["home"])
        away_team = str(fixture["away"])
        home_xg, away_xg = _match_expected_goals(home_team, away_team, team_strengths)
        outcome_model = simulate_match(home_team, away_team, home_xg, away_xg, simulations=2200)
        models.append(
            {
                "date": fixture.get("date", datetime.utcnow().isoformat()),
                "home": home_team,
                "away": away_team,
                "home_xg": home_xg,
                "away_xg": away_xg,
                "prob_home": float(outcome_model["prob_home"]),
                "prob_draw": float(outcome_model["prob_draw"]),
            }
        )
    return models


def _sample_goals(xg: float, rng: random.Random) -> int:
    mean = max(0.0, float(xg))
    stdev = max(0.7, mean * 0.85)
    goals = int(round(rng.gauss(mean, stdev)))
    return max(0, goals)


def simulate_season(fixtures, team_strengths, simulations=5000):
    sims = max(100, int(simulations))
    fixture_models = _build_fixture_models(fixtures, team_strengths)

    rank_history: dict[str, list[int]] = defaultdict(list)
    points_history: dict[str, list[float]] = defaultdict(list)
    title_counts: dict[str, int] = defaultdict(int)
    top4_counts: dict[str, int] = defaultdict(int)
    relegation_counts: dict[str, int] = defaultdict(int)

    sorted_teams = sorted(team_strengths.keys())
    relegation_spots = 3

    for sim_index in range(sims):
        season_stats = _init_team_stats(team_strengths)

        for fixture in fixture_models:
            home_team = str(fixture["home"])
            away_team = str(fixture["away"])
            home_xg = float(fixture["home_xg"])
            away_xg = float(fixture["away_xg"])
            prob_home = float(fixture["prob_home"])
            prob_draw = float(fixture["prob_draw"])

            seed = f"{sim_index}:{home_team}:{away_team}:{fixture.get('date', datetime.utcnow().isoformat())}"
            rng = random.Random(seed)
            draw = rng.random()

            if draw < prob_home:
                home_goals = max(1, _sample_goals(home_xg + 0.2, rng))
                away_goals = _sample_goals(away_xg - 0.15, rng)
                if home_goals <= away_goals:
                    home_goals = away_goals + 1
            elif draw < (prob_home + prob_draw):
                goal_value = max(0, int(round((home_xg + away_xg) / 2.4)))
                home_goals = goal_value
                away_goals = goal_value
            else:
                home_goals = _sample_goals(home_xg - 0.1, rng)
                away_goals = max(1, _sample_goals(away_xg + 0.2, rng))
                if away_goals <= home_goals:
                    away_goals = home_goals + 1

            _apply_match_result(season_stats, home_team, away_team, home_goals, away_goals)

        table = _sorted_table(season_stats)
        total_teams = len(table)

        for rank, row in enumerate(table, start=1):
            team_name = row[0]
            row_stats = row[1]
            rank_history[team_name].append(rank)
            points_history[team_name].append(float(row_stats["points"]))

            if rank == 1:
                title_counts[team_name] += 1
            if rank <= 4:
                top4_counts[team_name] += 1
            if rank > (total_teams - relegation_spots):
                relegation_counts[team_name] += 1

    projection_rows = []
    for team_name in sorted_teams:
        ranks = sorted(rank_history[team_name])
        points_values = points_history[team_name]
        expected_points = sum(points_values) / len(points_values) if points_values else 0.0
        expected_rank = sum(ranks) / len(ranks) if ranks else 0.0
        likely_rank = _most_common(ranks) if ranks else 0
        rank_10 = _percentile(ranks, 0.10)
        rank_90 = _percentile(ranks, 0.90)

        projection_rows.append(
            {
                "team": team_name,
                "expected_points": round(expected_points, 2),
                "expected_rank": round(expected_rank, 2),
                "most_likely_rank": likely_rank,
                "rank_range_10_90": f"{rank_10}-{rank_90}",
                "title_probability": round(title_counts[team_name] / sims, 4),
                "top4_probability": round(top4_counts[team_name] / sims, 4),
                "relegation_probability": round(relegation_counts[team_name] / sims, 4),
            }
        )

    projection_rows.sort(key=lambda row: row["expected_rank"])
    return projection_rows
