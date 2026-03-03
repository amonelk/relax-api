from fastapi import APIRouter, File, Form, Query, Request, UploadFile
from pydantic import BaseModel, Field
from typing import Literal

from app.core.errors import AppError
from app.core.response import ok_response
from app.schemas.common import ApiResponse
from app.loaders.tool_loader import get_executor

router = APIRouter()
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


# ========== 生成二维码 ==========
@router.get(
    "/generate",
    response_model=ApiResponse,
    summary="生成二维码",
    description="根据文本生成二维码图片",
)
async def generate_qrcode(
    text: str = Query(..., description="二维码内容"),
    size: int = Query(default=300, ge=100, le=1000, description="图片尺寸 (px)"),
    format: str = Query(default="png", description="输出格式: png/jpeg/webp"),
) -> dict:
    payload = {
        "text": text,
        "size": size,
        "format": format,
    }
    result = get_executor("qrcode")("generate", payload)
    return ok_response(data=result, message="qrcode generated")


# ========== 解析二维码 ==========
@router.post(
    "/decode",
    response_model=ApiResponse,
    summary="解析二维码",
    description="从图片中解析二维码内容",
)
async def decode_qrcode(
    file: UploadFile = File(..., description="包含二维码的图片"),
) -> dict:
    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise AppError(
            code=41300,
            message="Uploaded file is too large. Max size is 10MB.",
            http_status=413,
        )

    payload = {
        "file_bytes": file_bytes,
        "filename": file.filename or "upload.bin",
    }
    result = get_executor("qrcode")("decode", payload)
    return ok_response(data=result, message="qrcode decoded")
