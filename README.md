# FPL Predictions

Full-stack FPL predictions app built with FastAPI (backend) and React + Vite (frontend).

## Features
- Pulls official FPL bootstrap data from `https://fantasy.premierleague.com/api/bootstrap-static/`
- Baseline deterministic prediction model
- Predictions endpoint with filtering and search
- React UI with search, team filter, position filter, and price range
- Optional API-Football server-side client (key-based)

## Project Structure
- `backend/` FastAPI API
- `frontend/` React + Vite app

## Local Development

### Backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Environment Variables

### Backend (`backend/.env`)
- `APIFOOTBALL_API_KEY` (optional)
- `BACKEND_CORS_ORIGINS` (optional comma-separated origins)

### Frontend (`frontend/.env`)
- `VITE_API_BASE_URL` (default `http://localhost:8000`)

## Render Deployment (Backend)
A Render Blueprint file is included at `backend/render.yaml`.

1. In Render, create a Blueprint service from this repository.
2. Select `backend/render.yaml`.
3. Set env vars in Render dashboard as needed:
   - `APIFOOTBALL_API_KEY` (optional)
   - `BACKEND_CORS_ORIGINS` (optional, comma-separated)
4. Deploy.

Health check endpoint: `GET /health`
API health endpoint: `GET /health`

## API Endpoints
- `GET /health`
- `GET /fpl/bootstrap`
- `GET /predictions?search=&team_id=&position=&min_price=&max_price=&limit=`
