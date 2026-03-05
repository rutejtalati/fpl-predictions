import math
import random
from collections import Counter


def poisson_pmf(k: int, lam: float) -> float:
    if k < 0:
        return 0.0
    lam = max(0.01, float(lam))
    return math.exp(-lam) * (lam**k) / math.factorial(k)


def score_probabilities(home_xg: float, away_xg: float, max_goals: int = 6) -> list[dict[str, float | str]]:
    grid: list[dict[str, float | str]] = []
    for home_goals in range(max_goals + 1):
        p_home = poisson_pmf(home_goals, home_xg)
        for away_goals in range(max_goals + 1):
            p_away = poisson_pmf(away_goals, away_xg)
            p = p_home * p_away
            grid.append({"score": f"{home_goals}-{away_goals}", "p": p})

    total = sum(float(row["p"]) for row in grid)
    if total > 0:
        for row in grid:
            row["p"] = float(row["p"]) / total

    grid.sort(key=lambda row: float(row["p"]), reverse=True)
    return grid


def _sample_poisson(lam: float, rng: random.Random) -> int:
    lam = max(0.01, float(lam))
    if lam > 8.0:
        draw = int(round(rng.gauss(lam, math.sqrt(lam))))
        return max(0, draw)

    threshold = math.exp(-lam)
    k = 0
    product = 1.0
    while product > threshold:
        k += 1
        product *= rng.random()
    return k - 1


def _score_from_counter(counter: Counter[tuple[int, int]], simulations: int) -> list[dict[str, float | str]]:
    rows = []
    for score, count in counter.most_common(3):
        rows.append({"score": f"{score[0]}-{score[1]}", "p": round(count / float(simulations), 4)})
    return rows


def simulate_match(home_team, away_team, home_xg, away_xg, simulations=10000):
    seed_input = f"{home_team}:{away_team}:{round(float(home_xg), 3)}:{round(float(away_xg), 3)}:{int(simulations)}"
    rng = random.Random(seed_input)

    sims = max(1000, int(simulations))
    home_wins = 0
    draws = 0
    away_wins = 0
    over25 = 0
    btts = 0
    score_counter: Counter[tuple[int, int]] = Counter()

    for _ in range(sims):
        home_goals = _sample_poisson(home_xg, rng)
        away_goals = _sample_poisson(away_xg, rng)
        score_counter[(home_goals, away_goals)] += 1

        if home_goals > away_goals:
            home_wins += 1
        elif home_goals == away_goals:
            draws += 1
        else:
            away_wins += 1

        if (home_goals + away_goals) >= 3:
            over25 += 1
        if home_goals > 0 and away_goals > 0:
            btts += 1

    score_grid = score_probabilities(float(home_xg), float(away_xg), max_goals=6)
    top_scores = _score_from_counter(score_counter, sims)
    most_likely_score = top_scores[0]["score"] if top_scores else str(score_grid[0]["score"])

    return {
        "prob_home": round(home_wins / sims, 4),
        "prob_draw": round(draws / sims, 4),
        "prob_away": round(away_wins / sims, 4),
        "xg_home": round(float(home_xg), 3),
        "xg_away": round(float(away_xg), 3),
        "most_likely_score": most_likely_score,
        "top_scores": top_scores,
        "over25_p": round(over25 / sims, 4),
        "btts_p": round(btts / sims, 4),
    }
