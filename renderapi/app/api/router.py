from fastapi import APIRouter

from app.api.routes import markitdown

api_router = APIRouter()
api_router.include_router(markitdown.router, prefix="/tools/markitdown", tags=["markitdown"])
