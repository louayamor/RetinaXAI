from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger

from app.api.routes import health, train, status, metrics, predict
from app.api.dependencies import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(f"starting {settings.app_name} v{settings.app_version}")
    logger.info(f"environment: {settings.app_env}")
    yield
    logger.info("shutting down mlops service")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(train.router, tags=["training"])
    app.include_router(status.router, tags=["status"])
    app.include_router(metrics.router, tags=["metrics"])
    app.include_router(predict.router, tags=["predict"])

    return app


app = create_app()
