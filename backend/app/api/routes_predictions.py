from fastapi import APIRouter, Query

from app.schemas.prediction import PlayerPrediction
from app.services.fpl_client import fetch_bootstrap_data
from app.services.predictor import build_player_predictions, filter_predictions

router = APIRouter(tags=["predictions"])


@router.get("/predictions")
def get_predictions(
    search: str | None = Query(default=None),
    team_id: int | None = Query(default=None),
    position: str | None = Query(default=None),
    min_price: float | None = Query(default=None),
    max_price: float | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
) -> dict:
    payload = fetch_bootstrap_data()
    predictions = build_player_predictions(payload)
    filtered = filter_predictions(
        predictions=predictions,
        search=search,
        team_id=team_id,
        position=position,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
    )

    typed_rows = [PlayerPrediction(**row).model_dump() for row in filtered]
    return {"count": len(typed_rows), "predictions": typed_rows}
