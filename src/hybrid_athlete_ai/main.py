from contextlib import asynccontextmanager

from fastapi import FastAPI

from hybrid_athlete_ai.api.coach_routes import router as coach_router
from hybrid_athlete_ai.api.routes import router
from hybrid_athlete_ai.config import settings
from hybrid_athlete_ai.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(router, prefix="/api/v1")
    app.include_router(coach_router, prefix="/api/v1")
    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run("hybrid_athlete_ai.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
