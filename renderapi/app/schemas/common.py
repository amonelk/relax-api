from typing import Any, Dict

from pydantic import BaseModel, Field


class ToolExecuteRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Tool specific input.")


class ApiResponse(BaseModel):
    code: int
    message: str
    data: Any
    request_id: str
