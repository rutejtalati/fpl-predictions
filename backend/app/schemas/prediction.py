from pydantic import BaseModel


class PlayerPrediction(BaseModel):
    id: int
    name: str
    team: str
    position: str
    price: float
    predicted_points: float
    chance_playing: int
    form: float
    points_per_game: float
