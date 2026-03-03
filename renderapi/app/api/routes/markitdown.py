from fastapi import APIRouter, File, Form, Request, UploadFile
from pydantic import BaseModel, Field
from typing import Literal

from app.core.errors import AppError
from app.core.response import ok_response
from app.schemas.common import ApiResponse
from app.loaders.tool_loader import get_executor

router = APIRouter()
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


class MarkItDownPayload(BaseModel):
    text: str | None = Field(default=None, description="Inline text content to convert.")
    suffix: str = Field(default=".txt", description="Temporary file suffix for inline text mode.")
    format_mode: Literal["raw", "enhanced", "strict"] = Field(
        default="raw",
        description="Markdown post-process mode: raw/enhanced/strict.",
    )
    use_plugins: bool = Field(default=False, description="Whether to pass --use-plugins.")
    docintel_endpoint: str | None = Field(
        default=None,
        description="Document intelligence endpoint. If provided, docintel mode is auto enabled.",
    )


class MarkItDownExecuteRequest(BaseModel):
    payload: MarkItDownPayload


@router.post(
    "/execute",
    response_model=ApiResponse,
    summary="文本/文件转换",
    description="支持 JSON 文本转换与 multipart/form-data 文件上传转换（统一入口）。",
)
async def execute_markitdown(
    request: Request,
    file: UploadFile | None = File(default=None),
    text: str | None = Form(default=None),
    suffix: str = Form(default=".txt"),
    format_mode: str = Form(default="raw"),
    use_plugins: bool = Form(default=False),
    docintel_endpoint: str | None = Form(default=None),
) -> dict:
    content_type = (request.headers.get("content-type") or "").lower()

    if "application/json" in content_type:
        body = await request.json()
        payload = MarkItDownExecuteRequest.model_validate(body).payload.model_dump()
    else:
        payload = {
            "text": text,
            "suffix": suffix,
            "format_mode": format_mode,
            "use_plugins": use_plugins,
            "docintel_endpoint": docintel_endpoint,
        }
        if file is not None:
            file_bytes = await file.read()
            if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
                raise AppError(
                    code=41300,
                    message="Uploaded file is too large. Max size is 10MB.",
                    http_status=413,
                )
            payload["file_bytes"] = file_bytes
            payload["filename"] = file.filename or "upload.bin"

    result = get_executor("markitdown")(payload)
    return ok_response(data=result, message="markitdown executed")
