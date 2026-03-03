from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path


def _load_upstream_markitdown_class():
    tool_root = Path(__file__).resolve().parents[2]
    upstream_src = tool_root / "upstream" / "packages" / "markitdown" / "src"
    if not upstream_src.exists():
        raise FileNotFoundError(
            f"upstream source not found: {upstream_src}. Run scripts/sync_sources.py first."
        )
    if str(upstream_src) not in sys.path:
        sys.path.insert(0, str(upstream_src))
    try:
        from markitdown import MarkItDown  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"failed to import upstream markitdown from: {upstream_src}") from exc
    return MarkItDown


def _create_markitdown_client(payload: dict):
    MarkItDown = _load_upstream_markitdown_class()
    kwargs = {"enable_plugins": bool(payload.get("use_plugins", False))}
    endpoint = payload.get("docintel_endpoint")
    if endpoint is not None and str(endpoint).strip():
        kwargs["docintel_endpoint"] = str(endpoint).strip()
    return MarkItDown(**kwargs)


def _normalize_bullet_line(line: str) -> str:
    stripped = line.lstrip()
    indent = " " * (len(line) - len(stripped))
    if stripped.startswith("•"):
        content = stripped[1:].strip()
        return f"{indent}- {content}" if content else line
    if re.match(r"^[-*]\S", stripped):
        return f"{indent}{stripped[0]} {stripped[1:].strip()}"
    return line


def _enhance_markdown(markdown: str) -> str:
    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    out: list[str] = []
    blank_count = 0

    for raw in lines:
        line = _normalize_bullet_line(raw.rstrip())
        stripped = line.strip()

        if re.match(r"^\d+\)", stripped):
            line = re.sub(r"^(\d+)\)\s*", r"\1. ", line)
            stripped = line.strip()

        if not stripped:
            blank_count += 1
            if blank_count <= 2:
                out.append("")
            continue

        blank_count = 0
        out.append(line)

    return "\n".join(out).strip() + "\n"


def _strict_markdown(markdown: str) -> str:
    enhanced = _enhance_markdown(markdown)
    lines = enhanced.split("\n")
    merged: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            merged.append(line)
            continue

        if not merged:
            merged.append(line)
            continue

        prev = merged[-1].strip()
        is_paragraph_like = prev and not prev.startswith(("#", "-", "*", "|")) and not re.match(
            r"^\d+\.\s", prev
        )
        starts_like_continuation = bool(re.match(r"^[a-z0-9(（]", stripped))
        prev_ends_hard = bool(re.search(r"[.!?:;。！？：；]$", prev))

        if is_paragraph_like and starts_like_continuation and not prev_ends_hard:
            merged[-1] = f"{merged[-1].rstrip()} {stripped}"
        else:
            merged.append(line)

    return "\n".join(merged).strip() + "\n"


def _format_markdown(markdown: str, format_mode: str) -> str:
    if format_mode == "raw":
        return markdown
    if format_mode == "enhanced":
        return _enhance_markdown(markdown)
    if format_mode == "strict":
        return _strict_markdown(markdown)
    raise ValueError("format_mode 必须是 raw/enhanced/strict")


def execute_markitdown(payload: dict) -> dict:
    md = _create_markitdown_client(payload)
    format_mode = str(payload.get("format_mode", "raw")).lower()

    file_bytes = payload.get("file_bytes")

    if file_bytes is not None:
        if not isinstance(file_bytes, (bytes, bytearray)):
            raise ValueError("file_bytes must be bytes")
        filename = str(payload.get("filename", "upload.bin"))
        suffix = Path(filename).suffix or ".bin"
        with tempfile.NamedTemporaryFile("wb", suffix=suffix, delete=True) as temp:
            temp.write(bytes(file_bytes))
            temp.flush()
            result = md.convert(temp.name)
            text_content = result.text_content
            source = f"upload:{filename}"
    else:
        raw_text = payload.get("text")
        text = raw_text if isinstance(raw_text, str) else ""
        suffix = str(payload.get("suffix", ".txt"))
        with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=True, encoding="utf-8") as temp:
            temp.write(text)
            temp.flush()
            result = md.convert(temp.name)
            text_content = result.text_content
            source = "inline-text"

    text_content = _format_markdown(text_content, format_mode=format_mode)

    return {
        "tool": "markitdown",
        "source": source,
        "format_mode": format_mode,
        "markdown": text_content,
    }
