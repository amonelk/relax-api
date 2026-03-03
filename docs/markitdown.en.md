# markitdown API Documentation

## 1. Overview

The `markitdown` service converts input text or uploaded files into Markdown through a single HTTP endpoint.

- **Base URL**: `https://relax-api.onrender.com`
- **Endpoint**: `POST /api/v1/tools/markitdown/execute`
- Supported request types:
  - `application/json` (text conversion)
  - `multipart/form-data` (file upload conversion)

## 2. Endpoints

### 2.1 Execute Conversion

- **Method**: `POST`
- **Path**: `/api/v1/tools/markitdown/execute`
- **Capabilities**:
  - Text input (`payload.text` or form `text`)
  - File input (form `file`)
  - Markdown post-formatting (`raw/enhanced/strict`)
  - Optional plugin enablement (`use_plugins`)
  - Optional docintel enablement (auto-enabled when `docintel_endpoint` is non-empty)

## 3. Request Parameters

### 3.1 JSON Mode (`Content-Type: application/json`)

Request body:

```json
{
  "payload": {
    "text": "string | null",
    "suffix": ".txt",
    "format_mode": "raw | enhanced | strict",
    "use_plugins": false,
    "docintel_endpoint": "string | null"
  }
}
```

Field details:

| Field | Type | Required | Default | Constraints |
|---|---|---:|---|---|
| `payload` | object | Yes | - | Parameter container |
| `payload.text` | string \| null | No | `null` | Text content; treated as empty string if absent |
| `payload.suffix` | string | No | `.txt` | Temp file suffix |
| `payload.format_mode` | string | No | `raw` | Enum: `raw` / `enhanced` / `strict` |
| `payload.use_plugins` | bool | No | `false` | Enable plugins |
| `payload.docintel_endpoint` | string \| null | No | `null` | Auto-enables docintel when non-empty |

### 3.2 Multipart Mode (`Content-Type: multipart/form-data`)

Form fields:

| Field | Type | Required | Default | Constraints |
|---|---|---:|---|---|
| `file` | File | No | - | If provided, file conversion path is used |
| `text` | Text | No | `null` | Optional text fallback when no file |
| `suffix` | Text | No | `.txt` | Temp suffix for text mode |
| `format_mode` | Text | No | `raw` | Enum: `raw` / `enhanced` / `strict` |
| `use_plugins` | Text(bool) | No | `false` | `true` / `false` |
| `docintel_endpoint` | Text | No | `null` | Auto-enables docintel when non-empty |

Upload limit:

- Maximum file size for `file`: `10MB`
- Exceeding limit returns HTTP `413` with business code `41300`

## 4. Response Schema

Success response (unified envelope):

```json
{
  "code": 0,
  "message": "markitdown executed",
  "data": {
    "tool": "markitdown",
    "source": "inline-text",
    "format_mode": "enhanced",
    "markdown": "..."
  },
  "request_id": "uuid"
}
```

Field details:

| Field | Type | Description |
|---|---|---|
| `code` | int | `0` means success |
| `message` | string | Status message |
| `data.tool` | string | Always `markitdown` |
| `data.source` | string | `inline-text` or `upload:<filename>` |
| `data.format_mode` | string | Effective format mode |
| `data.markdown` | string | Converted Markdown content |
| `request_id` | string | Request trace ID |

## 5. Error Handling

Known behaviors:

| Scenario | HTTP Status | Business Code | Description |
|---|---:|---:|---|
| Uploaded file larger than 10MB | `413` | `41300` | `Uploaded file is too large. Max size is 10MB.` |
| Validation error (e.g., invalid `format_mode`) | `422` | - | FastAPI validation error format |
| Unhandled runtime exception | `500` | `50000` | `Internal server error: ...` |

Unified error envelope (`AppError` / global exception handler):

```json
{
  "code": 41300,
  "message": "Uploaded file is too large. Max size is 10MB.",
  "data": {},
  "request_id": "uuid"
}
```

## 6. Examples

### 6.1 JSON Text Conversion (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "text": "# hello from http",
      "suffix": ".md",
      "format_mode": "enhanced",
      "use_plugins": false,
      "docintel_endpoint": null
    }
  }'
```

### 6.2 File Upload Conversion (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -F "file=@/path/to/demo.pdf" \
  -F "format_mode=strict" \
  -F "use_plugins=false"
```

### 6.3 Python Example

```python
import requests

url = "https://relax-api.onrender.com/api/v1/tools/markitdown/execute"
resp = requests.post(
    url,
    json={
        "payload": {
            "text": "# Title",
            "format_mode": "enhanced",
            "use_plugins": False,
            "docintel_endpoint": None,
        }
    },
    timeout=60,
)
print(resp.status_code, resp.json())
```

## 7. Limits and Notes

- This document reflects current code behavior and does not cover all potential edge cases.
- `format_mode` only supports: `raw`, `enhanced`, `strict`.
- Docintel is enabled only when `docintel_endpoint` is non-empty.
- The API is designed for HTTP usage and does not expose local file output parameters.
