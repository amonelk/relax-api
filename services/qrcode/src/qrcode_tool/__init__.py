from __future__ import annotations

import base64
import io
from typing import Any

import qrcode
from PIL import Image

# 尝试导入 pyzbar，失败时禁用解码功能
try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False


def _generate(payload: dict) -> dict:
    """生成二维码"""
    text = payload["text"]
    size = payload.get("size", 300)
    format = payload.get("format", "png")

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size))

    output = io.BytesIO()
    mime_map = {"png": "image/png", "jpeg": "image/jpeg", "webp": "image/webp"}
    img.save(output, format=format.upper())

    result_b64 = base64.b64encode(output.getvalue()).decode("utf-8")

    return {
        "image": result_b64,
        "format": format,
        "mime_type": mime_map.get(format, "image/png"),
        "text": text,
        "size": size,
    }


def _decode(payload: dict) -> dict:
    """解析二维码"""
    if not HAS_PYZBAR:
        return {
            "error": "pyzbar not installed, decode feature unavailable",
            "results": [],
        }

    file_bytes = payload["file_bytes"]
    img = Image.open(io.BytesIO(file_bytes))

    decoded = pyzbar_decode(img)

    if not decoded:
        return {
            "error": "No QR code detected",
            "results": [],
        }

    results = [{"type": d.type, "data": d.data.decode("utf-8")} for d in decoded]

    return {
        "results": results,
        "count": len(results),
    }


def execute_qrcode(action: str, payload: dict) -> dict:
    """二维码处理执行器

    Args:
        action: 操作类型 (generate/decode)
        payload: 操作参数

    Returns:
        处理结果
    """
    handlers = {
        "generate": _generate,
        "decode": _decode,
    }

    handler = handlers.get(action)
    if not handler:
        raise ValueError(f"Unknown action: {action}")

    return handler(payload)
