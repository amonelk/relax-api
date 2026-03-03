from fastapi import FastAPI

from app.api.router import api_router
from app.core.errors import register_exception_handlers
from app.core.response import ok_response


def create_app() -> FastAPI:
    app = FastAPI(
        title="Render API Gateway",
        version="0.1.0",
        description="Unified API gateway for multiple integrated tools.",
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/healthz")
    def healthz() -> dict:
        return ok_response(data={"status": "healthy"})

    @app.get("/readyz")
    def readyz() -> dict:
        return ok_response(data={"status": "ready"})

    return app


app = create_app()
