from fastapi import APIRouter

from app.api.routes import markitdown, image, qrcode

api_router = APIRouter()
api_router.include_router(markitdown.router, prefix="/tools/markitdown", tags=["markitdown"])
api_router.include_router(image.router, prefix="/tools/image", tags=["image"])
api_router.include_router(qrcode.router, prefix="/tools/qrcode", tags=["qrcode"])
