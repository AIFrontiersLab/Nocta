from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analytics, dashboard, experiments, feedback, ideas, memory, prototypes, resurrections, runs, signals
from app.config.settings import get_settings
from app.database import init_db
from app.utils.logging import setup_logging


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)
    init_db()

    app = FastAPI(title="Vectra FutureLab", version="0.2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(dashboard.router, prefix="/api")
    app.include_router(signals.router, prefix="/api")
    app.include_router(experiments.router, prefix="/api")
    app.include_router(ideas.router, prefix="/api")
    app.include_router(prototypes.router, prefix="/api")
    app.include_router(resurrections.router, prefix="/api")
    app.include_router(memory.router, prefix="/api")
    app.include_router(runs.router, prefix="/api")
    app.include_router(feedback.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "product": "Vectra FutureLab", "version": "0.2.0"}

    return app
