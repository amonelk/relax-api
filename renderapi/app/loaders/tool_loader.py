from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable

from app.core.errors import ToolNotFoundError


REPO_ROOT = Path(__file__).resolve().parents[3]
TOOL_CORE_PATHS = {
    "markitdown": REPO_ROOT / "services" / "markitdown" / "src" / "markitdown_tool" / "core.py",
    "image": REPO_ROOT / "services" / "image" / "src" / "image_tool" / "core.py",
    "qrcode": REPO_ROOT / "services" / "qrcode" / "src" / "qrcode_tool" / "core.py",
}
TOOL_FUNC_NAMES = {
    "markitdown": "execute_markitdown",
    "image": "execute_image",
    "qrcode": "execute_qrcode",
}
# 标记哪些工具需要 action 参数
MULTI_ACTION_TOOLS = {"image", "qrcode"}

_CACHE: dict[str, Callable[..., dict[str, Any]]] = {}


def _load_core_module(tool_name: str):
    core_path = TOOL_CORE_PATHS.get(tool_name)
    if not core_path or not core_path.exists():
        raise ToolNotFoundError(tool_name=tool_name)

    module_name = f"core_{tool_name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, core_path)
    if spec is None or spec.loader is None:
        raise ToolNotFoundError(tool_name=tool_name)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_executor(tool_name: str) -> Callable[..., dict[str, Any]]:
    """
    获取工具执行器。

    对于多 action 工具 (image, qrcode)，返回签名: (action: str, payload: dict) -> dict
    对于单 action 工具 (markitdown)，返回签名: (payload: dict) -> dict
    """
    if tool_name in _CACHE:
        return _CACHE[tool_name]

    module = _load_core_module(tool_name)
    function_name = TOOL_FUNC_NAMES.get(tool_name)
    if function_name is None:
        raise ToolNotFoundError(tool_name=tool_name)
    execute = getattr(module, function_name, None)
    if execute is None:
        raise ToolNotFoundError(tool_name=tool_name)
    _CACHE[tool_name] = execute
    return execute
