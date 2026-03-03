from fastapi import APIRouter, File, Form, Query, Request, UploadFile
from pydantic import BaseModel, Field
from typing import Literal

from app.core.errors import AppError
from app.core.response import ok_response
from app.schemas.common import ApiResponse
from app.loaders.tool_loader import get_executor

router = APIRouter()
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


class ImageCompressPayload(BaseModel):
    quality: int = Field(default=80, ge=1, le=100, description="压缩质量 1-100")


class ImageResizePayload(BaseModel):
    width: int | None = Field(default=None, ge=1, description="目标宽度")
    height: int | None = Field(default=None, ge=1, description="目标高度")
    fit: Literal["inside", "outside", "cover", "contain"] = Field(
        default="inside", description="缩放模式"
    )


class ImageConvertPayload(BaseModel):
    format: Literal["webp", "jpeg", "png", "avif"] = Field(
        ..., description="目标格式"
    )


class ImageWatermarkPayload(BaseModel):
    text: str = Field(..., description="水印文字")
    position: Literal["top-left", "top-right", "bottom-left", "bottom-right", "center"] = Field(
        default="bottom-right", description="水印位置"
    )


# ========== 压缩 ==========
@router.post(
    "/compress",
    response_model=ApiResponse,
    summary="图片压缩",
    description="压缩图片，支持 JPEG/PNG/WebP 格式",
)
async def compress_image(
    file: UploadFile = File(..., description="图片文件"),
    quality: int = Form(default=80, ge=1, le=100, description="压缩质量"),
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
        "content_type": file.content_type or "image/jpeg",
        "quality": quality,
    }
    result = get_executor("image")("compress", payload)
    return ok_response(data=result, message="image compressed")


# ========== 调整尺寸 ==========
@router.post(
    "/resize",
    response_model=ApiResponse,
    summary="调整图片尺寸",
    description="调整图片尺寸，支持保持比例或强制缩放",
)
async def resize_image(
    file: UploadFile = File(..., description="图片文件"),
    width: int | None = Form(default=None, ge=1, description="目标宽度"),
    height: int | None = Form(default=None, ge=1, description="目标高度"),
    fit: str = Form(default="inside", description="缩放模式: inside/outside/cover/contain"),
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
        "content_type": file.content_type or "image/jpeg",
        "width": width,
        "height": height,
        "fit": fit,
    }
    result = get_executor("image")("resize", payload)
    return ok_response(data=result, message="image resized")


# ========== 格式转换 ==========
@router.post(
    "/convert",
    response_model=ApiResponse,
    summary="图片格式转换",
    description="转换图片格式，支持 webp/jpeg/png/avif",
)
async def convert_image(
    file: UploadFile = File(..., description="图片文件"),
    format: str = Form(..., description="目标格式: webp/jpeg/png/avif"),
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
        "content_type": file.content_type or "image/jpeg",
        "format": format,
    }
    result = get_executor("image")("convert", payload)
    return ok_response(data=result, message="image converted")


# ========== 水印 ==========
@router.post(
    "/watermark",
    response_model=ApiResponse,
    summary="添加文字水印",
    description="为图片添加文字水印",
)
async def watermark_image(
    file: UploadFile = File(..., description="图片文件"),
    text: str = Form(..., description="水印文字"),
    position: str = Form(default="bottom-right", description="水印位置"),
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
        "content_type": file.content_type or "image/jpeg",
        "text": text,
        "position": position,
    }
    result = get_executor("image")("watermark", payload)
    return ok_response(data=result, message="watermark added")
