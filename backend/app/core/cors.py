from app.core.config import settings


def get_cors_origins() -> list[str]:
    defaults = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    raw = (settings.backend_cors_origins or "").strip()
    if not raw:
        return defaults

    out: list[str] = []
    for item in raw.split(","):
        origin = item.strip().rstrip("/")
        if origin and origin not in out:
            out.append(origin)

    for origin in defaults:
        if origin not in out:
            out.append(origin)

    return out
