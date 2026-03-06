import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import api_router
from app.core.errors import register_exception_handlers
from app.core.response import error_response, ok_response

_SKIP_AUTH_PATHS = {"/healthz", "/readyz"}


class RapidAPIAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret: str) -> None:
        super().__init__(app)
        self._secret = secret

    async def dispatch(self, request: Request, call_next):
        if request.url.path not in _SKIP_AUTH_PATHS:
            incoming = request.headers.get("X-RapidAPI-Proxy-Secret", "")
            if incoming != self._secret:
                return JSONResponse(
                    status_code=403,
                    content=error_response(code=40300, message="Forbidden: invalid or missing proxy secret."),
                )
        return await call_next(request)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Render API Gateway",
        version="0.1.0",
        description="Unified API gateway for multiple integrated tools.",
    )
    register_exception_handlers(app)

    secret = os.environ.get("RAPIDAPI_PROXY_SECRET", "")
    if secret:
        app.add_middleware(RapidAPIAuthMiddleware, secret=secret)

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/healthz")
    def healthz() -> dict:
        return ok_response(data={"status": "healthy"})

    @app.get("/readyz")
    def readyz() -> dict:
        return ok_response(data={"status": "ready"})

    return app


app = create_app()
