from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.response import error_response


class AppError(Exception):
    def __init__(self, code: int, message: str, http_status: int = 400) -> None:
        self.code = code
        self.message = message
        self.http_status = http_status
        super().__init__(message)


class ToolNotFoundError(AppError):
    def __init__(self, tool_name: str) -> None:
        super().__init__(code=40401, message=f"Tool '{tool_name}' not found.", http_status=404)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content=error_response(code=exc.code, message=exc.message),
        )

    @app.exception_handler(Exception)
    async def unknown_error_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=error_response(code=50000, message=f"Internal server error: {exc}"),
        )
