from __future__ import annotations

import math
import random
from typing import Any, Dict, List

try:
    import numpy as np
except Exception:
    np = None

DEFAULT_MU = 1.35


def _poisson_sample_knuth(lam: float) -> int:
    lam = max(0.0, float(lam))
    if lam == 0:
        return 0
    l = math.exp(-lam)
    k = 0
    p = 1.0
    while p > l:
        k += 1
        p *= random.random()
    return k - 1


def _mc_simulate(expected_home_goals: float, expected_away_goals: float, mc_runs: int) -> tuple[list[int], list[int]]:
    if np is not None:
        rng = np.random.default_rng()
        home_sim = rng.poisson(expected_home_goals, size=mc_runs).tolist()
        away_sim = rng.poisson(expected_away_goals, size=mc_runs).tolist()
        return home_sim, away_sim

    home_sim = [_poisson_sample_knuth(expected_home_goals) for _ in range(mc_runs)]
    away_sim = [_poisson_sample_knuth(expected_away_goals) for _ in range(mc_runs)]
    return home_sim, away_sim


def poisson_pmf(k: int, lam: float) -> float:
    if k < 0:
        return 0.0
    lam = max(0.0, float(lam))
    return math.exp(-lam) * (lam**k) / math.factorial(k)


def score_probability_table(expected_home_goals: float, expected_away_goals: float, max_goals: int = 5) -> List[List[float]]:
    home_probs = [poisson_pmf(i, expected_home_goals) for i in range(max_goals + 1)]
    away_probs = [poisson_pmf(j, expected_away_goals) for j in range(max_goals + 1)]
    return [[home_probs[i] * away_probs[j] for j in range(max_goals + 1)] for i in range(max_goals + 1)]


def estimate_team_strengths(standings_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    teams = standings_rows or []
    gfpg_vals = []
    for r in teams:
        played = max(1, int(r.get("matches_played", r.get("played", 0)) or 0))
        gf = float(r.get("goals_scored", r.get("gf", 0)) or 0.0)
        gfpg_vals.append(gf / played)
    league_average_goals_per_match = sum(gfpg_vals) / len(gfpg_vals) if gfpg_vals else DEFAULT_MU
    if league_average_goals_per_match <= 0:
        league_average_goals_per_match = DEFAULT_MU

    strengths: Dict[int, Dict[str, float]] = {}
    for r in teams:
        team_id = int(r.get("team_id", 0) or 0)
        if team_id <= 0:
            continue
        played = max(1, int(r.get("matches_played", r.get("played", 0)) or 0))
        gfpg = float(r.get("goals_scored", r.get("gf", 0)) or 0.0) / played
        gapg = float(r.get("goals_conceded", r.get("ga", 0)) or 0.0) / played
        team_attacking_power = gfpg / league_average_goals_per_match if league_average_goals_per_match > 0 else 1.0
        team_defensive_strength = gapg / league_average_goals_per_match if league_average_goals_per_match > 0 else 1.0
        strengths[team_id] = {
            "team_attacking_power": team_attacking_power if team_attacking_power > 0 else 1.0,
            "team_defensive_strength": team_defensive_strength if team_defensive_strength > 0 else 1.0,
            "home_performance": 0.0,
            "away_performance": 0.0,
            "recent_form_rating": 0.5,
        }

    return {"league_average_goals_per_match": league_average_goals_per_match, "teams": strengths}


def predict_fixture(home_team_id: int, away_team_id: int, strengths: Dict[str, Any]) -> Dict[str, Any]:
    league_average_goals_per_match = float(strengths.get("league_average_goals_per_match", DEFAULT_MU) or DEFAULT_MU)
    team_strengths = strengths.get("teams", {}) or {}
    home = team_strengths.get(
        int(home_team_id),
        {"team_attacking_power": 1.0, "team_defensive_strength": 1.0, "home_performance": 0.0, "away_performance": 0.0, "recent_form_rating": 0.5},
    )
    away = team_strengths.get(
        int(away_team_id),
        {"team_attacking_power": 1.0, "team_defensive_strength": 1.0, "home_performance": 0.0, "away_performance": 0.0, "recent_form_rating": 0.5},
    )

    home_team_attacking_power = float(home.get("team_attacking_power", 1.0) or 1.0)
    home_team_defensive_strength = float(home.get("team_defensive_strength", 1.0) or 1.0)
    away_team_attacking_power = float(away.get("team_attacking_power", 1.0) or 1.0)
    away_team_defensive_strength = float(away.get("team_defensive_strength", 1.0) or 1.0)

    expected_home_goals = max(0.05, league_average_goals_per_match * home_team_attacking_power * away_team_defensive_strength * 1.10)
    expected_away_goals = max(0.05, league_average_goals_per_match * away_team_attacking_power * home_team_defensive_strength)

    probability_grid = score_probability_table(expected_home_goals, expected_away_goals, max_goals=5)
    home_win_probability = 0.0
    draw_probability = 0.0
    away_win_probability = 0.0
    best = (0, 0, -1.0)
    for i in range(6):
        for j in range(6):
            v = probability_grid[i][j]
            if i > j:
                home_win_probability += v
            elif i == j:
                draw_probability += v
            else:
                away_win_probability += v
            if v > best[2]:
                best = (i, j, v)

    mc_runs = 20000
    home_sim, away_sim = _mc_simulate(expected_home_goals, expected_away_goals, mc_runs)
    total_sim = [h + a for h, a in zip(home_sim, away_sim)]

    home_win_probability = sum(1 for h, a in zip(home_sim, away_sim) if h > a) / mc_runs
    draw_probability = sum(1 for h, a in zip(home_sim, away_sim) if h == a) / mc_runs
    away_win_probability = sum(1 for h, a in zip(home_sim, away_sim) if h < a) / mc_runs

    avg_home_goals = sum(home_sim) / mc_runs
    avg_away_goals = sum(away_sim) / mc_runs
    exp_goals_total = avg_home_goals + avg_away_goals

    p_over_0_5 = sum(1 for t in total_sim if t > 0) / mc_runs
    p_over_1_5 = sum(1 for t in total_sim if t > 1) / mc_runs
    p_over_2_5 = sum(1 for t in total_sim if t > 2) / mc_runs
    p_over_3_5 = sum(1 for t in total_sim if t > 3) / mc_runs
    p_btts = sum(1 for h, a in zip(home_sim, away_sim) if h >= 1 and a >= 1) / mc_runs
    p_home_cs = sum(1 for a in away_sim if a == 0) / mc_runs
    p_away_cs = sum(1 for h in home_sim if h == 0) / mc_runs
    p_home_2plus = sum(1 for h in home_sim if h >= 2) / mc_runs
    p_away_2plus = sum(1 for a in away_sim if a >= 2) / mc_runs

    score_counts: Dict[tuple[int, int], int] = {}
    for h, a in zip(home_sim, away_sim):
        score_counts[(h, a)] = score_counts.get((h, a), 0) + 1
    ordered = sorted(score_counts.items(), key=lambda kv: kv[1], reverse=True)
    top_score_probabilities = []
    for (hs, as_), cnt in ordered[:3]:
        top_score_probabilities.append({"score": f"{hs}-{as_}", "probability": float(cnt / mc_runs)})
    most_likely_score = top_score_probabilities[0]["score"] if top_score_probabilities else f"{best[0]}-{best[1]}"
    p_most_likely_score = top_score_probabilities[0]["probability"] if top_score_probabilities else float(best[2])

    outcome = [home_win_probability, draw_probability, away_win_probability]
    outcome_entropy = -sum(p * math.log2(p) for p in outcome if p > 0)

    return {
        "home_win_probability": round(home_win_probability, 4),
        "draw_probability": round(draw_probability, 4),
        "away_win_probability": round(away_win_probability, 4),
        "expected_home_goals": round(expected_home_goals, 4),
        "expected_away_goals": round(expected_away_goals, 4),
        "most_likely_score": most_likely_score,
        "top_score_probabilities": top_score_probabilities,
        "team_strength": {
            "home_team": {
                "team_attacking_power": round(home_team_attacking_power, 4),
                "team_defensive_strength": round(home_team_defensive_strength, 4),
                "home_performance": round(float(home.get("home_performance", 0.0) or 0.0), 4),
                "away_performance": round(float(home.get("away_performance", 0.0) or 0.0), 4),
                "recent_form_rating": round(float(home.get("recent_form_rating", 0.5) or 0.5), 4),
            },
            "away_team": {
                "team_attacking_power": round(away_team_attacking_power, 4),
                "team_defensive_strength": round(away_team_defensive_strength, 4),
                "home_performance": round(float(away.get("home_performance", 0.0) or 0.0), 4),
                "away_performance": round(float(away.get("away_performance", 0.0) or 0.0), 4),
                "recent_form_rating": round(float(away.get("recent_form_rating", 0.5) or 0.5), 4),
            },
        },
        # Additional metrics preserved from previous payload:
        "mc_runs": mc_runs,
        "exp_home_goals": round(avg_home_goals, 4),
        "exp_away_goals": round(avg_away_goals, 4),
        "exp_goals_total": round(exp_goals_total, 4),
        "p_over_0_5": round(p_over_0_5, 4),
        "p_over_1_5": round(p_over_1_5, 4),
        "p_over_2_5": round(p_over_2_5, 4),
        "p_over_3_5": round(p_over_3_5, 4),
        "p_btts": round(p_btts, 4),
        "p_home_cs": round(p_home_cs, 4),
        "p_away_cs": round(p_away_cs, 4),
        "p_home_2plus": round(p_home_2plus, 4),
        "p_away_2plus": round(p_away_2plus, 4),
        "p_most_likely_score": round(p_most_likely_score, 4),
        "outcome_entropy": round(float(outcome_entropy), 4),
        "expected_goal_diff": round(expected_home_goals - expected_away_goals, 4),
    }
