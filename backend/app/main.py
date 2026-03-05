from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_fpl import router as fpl_router
from app.api.routes_health import router as health_router
from app.api.routes_predictions import router as predictions_router
from app.core.cors import get_cors_origins

app = FastAPI(title="FPL Predictions API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(fpl_router)
app.include_router(predictions_router)
