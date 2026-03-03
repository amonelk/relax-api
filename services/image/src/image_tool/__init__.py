from __future__ import annotations

import base64
import io
from typing import Any

from PIL import Image, ImageDraw, ImageFont


def _get_output_format(content_type: str) -> str:
    """从 content_type 获取输出格式"""
    format_map = {
        "image/jpeg": "JPEG",
        "image/png": "PNG",
        "image/webp": "WEBP",
        "image/avif": "AVIF",
    }
    return format_map.get(content_type, "JPEG")


def _image_to_base64(img: Image.Image, format: str) -> str:
    """将图片转换为 base64 字符串"""
    output = io.BytesIO()
    if format == "JPEG" and img.mode == "RGBA":
        img = img.convert("RGB")
    img.save(output, format=format)
    return base64.b64encode(output.getvalue()).decode("utf-8")


def _compress(payload: dict) -> dict:
    """压缩图片"""
    file_bytes = payload["file_bytes"]
    quality = payload.get("quality", 80)
    content_type = payload.get("content_type", "image/jpeg")

    img = Image.open(io.BytesIO(file_bytes))
    fmt = _get_output_format(content_type)

    output = io.BytesIO()
    if fmt == "PNG":
        img.save(output, format=fmt, optimize=True)
    else:
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.save(output, format=fmt, quality=quality, optimize=True)

    result_b64 = base64.b64encode(output.getvalue()).decode("utf-8")
    original_size = len(file_bytes)
    compressed_size = len(output.getvalue())

    return {
        "image": result_b64,
        "format": fmt.lower(),
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": round(1 - compressed_size / original_size, 2) if original_size > 0 else 0,
    }


def _resize(payload: dict) -> dict:
    """调整图片尺寸"""
    file_bytes = payload["file_bytes"]
    width = payload.get("width")
    height = payload.get("height")
    fit = payload.get("fit", "inside")
    content_type = payload.get("content_type", "image/jpeg")

    img = Image.open(io.BytesIO(file_bytes))
    original_w, original_h = img.size
    fmt = _get_output_format(content_type)

    # 计算目标尺寸
    if width and height:
        if fit == "cover":
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        else:  # inside - 保持比例
            ratio = min(width / original_w, height / original_h)
            new_size = (int(original_w * ratio), int(original_h * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
    elif width:
        ratio = width / original_w
        new_size = (width, int(original_h * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    elif height:
        ratio = height / original_h
        new_size = (int(original_w * ratio), height)
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    result_b64 = _image_to_base64(img, fmt)
    new_w, new_h = img.size

    return {
        "image": result_b64,
        "format": fmt.lower(),
        "original_size": {"width": original_w, "height": original_h},
        "new_size": {"width": new_w, "height": new_h},
    }


def _convert(payload: dict) -> dict:
    """转换图片格式"""
    file_bytes = payload["file_bytes"]
    target_format = payload["format"].lower()
    content_type = payload.get("content_type", "image/jpeg")

    img = Image.open(io.BytesIO(file_bytes))

    format_map = {
        "jpeg": ("JPEG", "image/jpeg"),
        "png": ("PNG", "image/png"),
        "webp": ("WEBP", "image/webp"),
        "avif": ("AVIF", "image/avif"),
    }

    fmt, mime = format_map.get(target_format, ("JPEG", "image/jpeg"))

    if fmt == "JPEG" and img.mode == "RGBA":
        img = img.convert("RGB")

    result_b64 = _image_to_base64(img, fmt)

    return {
        "image": result_b64,
        "format": target_format,
        "mime_type": mime,
    }


def _watermark(payload: dict) -> dict:
    """添加文字水印"""
    file_bytes = payload["file_bytes"]
    text = payload["text"]
    position = payload.get("position", "bottom-right")
    content_type = payload.get("content_type", "image/jpeg")

    img = Image.open(io.BytesIO(file_bytes)).convert("RGBA")
    draw = ImageDraw.Draw(img)
    fmt = _get_output_format(content_type)

    # 尝试加载字体，失败则用默认
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()

    # 获取文字尺寸
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # 计算位置
    img_w, img_h = img.size
    padding = 20
    positions = {
        "top-left": (padding, padding),
        "top-right": (img_w - text_w - padding, padding),
        "bottom-left": (padding, img_h - text_h - padding),
        "bottom-right": (img_w - text_w - padding, img_h - text_h - padding),
        "center": ((img_w - text_w) // 2, (img_h - text_h) // 2),
    }
    x, y = positions.get(position, positions["bottom-right"])

    # 绘制半透明背景 + 文字
    draw.rectangle([x - 5, y - 5, x + text_w + 5, y + text_h + 5], fill=(0, 0, 0, 128))
    draw.text((x, y), text, fill=(255, 255, 255, 200), font=font)

    result_b64 = _image_to_base64(img, fmt if fmt != "JPEG" else "PNG")

    return {
        "image": result_b64,
        "format": "png" if fmt == "JPEG" else fmt.lower(),
        "text": text,
        "position": position,
    }


def execute_image(action: str, payload: dict) -> dict:
    """图片处理执行器

    Args:
        action: 操作类型 (compress/resize/convert/watermark)
        payload: 操作参数

    Returns:
        处理结果
    """
    handlers = {
        "compress": _compress,
        "resize": _resize,
        "convert": _convert,
        "watermark": _watermark,
    }

    handler = handlers.get(action)
    if not handler:
        raise ValueError(f"Unknown action: {action}")

    return handler(payload)
