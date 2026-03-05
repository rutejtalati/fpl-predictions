from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

from app.services.match_simulator import simulate_match
from app.services.season_simulator import simulate_season


router = APIRouter(prefix="/api/league", tags=["league-predictions"])


LEAGUE_TEAM_MAP = {
    "epl": [
        "Arsenal","Aston Villa","Bournemouth","Brentford","Brighton","Chelsea",
        "Crystal Palace","Everton","Fulham","Liverpool","Man City","Man United",
        "Newcastle","Nottingham","Spurs","West Ham","Wolves","Leicester",
        "Southampton","Ipswich",
    ],
    "laliga": [
        "Real Madrid","Barcelona","Atletico","Girona","Athletic","Real Sociedad",
        "Betis","Villarreal","Valencia","Sevilla","Getafe","Osasuna","Alaves",
        "Celta","Mallorca","Rayo","Las Palmas","Espanyol","Leganes","Valladolid",
    ],
    "ligue1": [
        "PSG","Marseille","Monaco","Lille","Lyon","Lens","Rennes","Nice",
        "Strasbourg","Reims","Nantes","Brest","Montpellier","Toulouse",
        "Le Havre","Auxerre","Angers","Saint-Etienne",
    ],
    "seriea": [
        "Inter","Milan","Juventus","Napoli","Atalanta","Roma","Lazio",
        "Fiorentina","Bologna","Torino","Genoa","Udinese","Monza","Lecce",
        "Verona","Cagliari","Empoli","Parma","Como","Venezia",
    ],
}


def _stable_unit(name: str) -> float:
    numeric = sum(ord(ch) for ch in name)
    return (numeric % 100) / 100.0


def _build_team_strengths(teams: list[str]) -> dict[str, dict[str, float]]:
    strengths: dict[str, dict[str, float]] = {}

    for team_name in teams:
        unit = _stable_unit(team_name)

        attack = 0.85 + unit * 0.5
        defense = 0.90 + (1.0 - unit) * 0.35
        recent_form = (unit - 0.5) * 1.2

        strengths[team_name] = {
            "attack": round(attack, 3),
            "defense": round(defense, 3),
            "recent_form": round(recent_form, 3),
        }

    return strengths


def _build_upcoming_fixtures(teams: list[str], max_matches: int = 12) -> list[dict[str, str]]:
    fixtures: list[dict[str, str]] = []

    start = datetime.now(timezone.utc).date() + timedelta(days=1)

    team_count = len(teams)
    index = 0

    for matchday in range(1, 8):

        for i in range(0, team_count - 1, 2):

            home = teams[(i + matchday) % team_count]
            away = teams[(i + matchday + 1) % team_count]

            if home == away:
                continue

            kickoff = datetime.combine(
                start + timedelta(days=index),
                datetime.min.time(),
                tzinfo=timezone.utc,
            )

            fixtures.append(
                {
                    "date": kickoff.isoformat(),
                    "home": home,
                    "away": away,
                }
            )

            index += 1

            if len(fixtures) >= max_matches:
                return fixtures

    return fixtures


def _predict_league(league_key: str, label: str) -> dict:

    teams = LEAGUE_TEAM_MAP[league_key]

    strengths = _build_team_strengths(teams)

    fixtures = _build_upcoming_fixtures(teams, max_matches=14)

    matches = []

    for fixture in fixtures:

        home = fixture["home"]
        away = fixture["away"]

        home_strength = strengths[home]
        away_strength = strengths[away]

        home_xg = max(
            0.35,
            1.15
            + (home_strength["attack"] - 1.0) * 0.7
            - (away_strength["defense"] - 1.0) * 0.5
            + 0.22,
        )

        away_xg = max(
            0.30,
            1.05
            + (away_strength["attack"] - 1.0) * 0.65
            - (home_strength["defense"] - 1.0) * 0.5,
        )

        sim = simulate_match(home, away, home_xg, away_xg, simulations=10000)

        confidence = abs(float(sim["prob_home"]) - float(sim["prob_away"])) + 0.15
        confidence = min(0.98, confidence)

        matches.append(
            {
                "date": fixture["date"],
                "home": home,
                "away": away,
                "xg_home": sim["xg_home"],
                "xg_away": sim["xg_away"],
                "p_home": sim["prob_home"],
                "p_draw": sim["prob_draw"],
                "p_away": sim["prob_away"],
                "most_likely_score": sim["most_likely_score"],
                "top_scores": sim["top_scores"],
                "over25_p": sim["over25_p"],
                "btts_p": sim["btts_p"],
                "confidence": round(confidence, 4),
            }
        )

    table_projection = simulate_season(fixtures, strengths, simulations=1200)

    return {
        "league": label,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "matches": matches,
        "table_projection": table_projection,
    }


@router.get("/epl/predictions")
def predictions_epl() -> dict:
    return _predict_league("epl", "EPL")


@router.get("/laliga/predictions")
def predictions_laliga() -> dict:
    return _predict_league("laliga", "La Liga")


@router.get("/ligue1/predictions")
def predictions_ligue1() -> dict:
    return _predict_league("ligue1", "Ligue 1")


@router.get("/seriea/predictions")
def predictions_seriea() -> dict:
    return _predict_league("seriea", "Serie A")