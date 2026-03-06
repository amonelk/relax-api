# markitdown API Documentation

## 1. Overview

The `markitdown` service converts text or uploaded files into Markdown through a single HTTP endpoint.

- **Base URL**: `https://relax-api.onrender.com`
- **Endpoint**: `POST /api/v1/tools/markitdown/execute`
- **Supported request types**:
  - `application/json` — text conversion
  - `multipart/form-data` — file upload conversion

---

## 2. Endpoints

### `POST /api/v1/tools/markitdown/execute` — Execute Conversion

**Description**: Convert text or an uploaded file to Markdown. Provide at least one of `file` or `text`. Max file size: 10MB.

**Capabilities**:
- Text input (`text` field)
- File upload (`file` field): supports PDF, Word, PPT, Excel, and more
- Markdown post-formatting (`raw` / `enhanced` / `strict`)
- Optional plugin enablement (`use_plugins`)
- Optional Document Intelligence (`docintel_endpoint`)

---

#### Mode 1 — JSON (`Content-Type: application/json`)

**Request Parameters**

| Field | Type | Required | Default | Constraints |
|---|---|---|---|---|
| `payload.text` | string \| null | No | `null` | Text content to convert |
| `payload.suffix` | string | No | `.txt` | Temp file suffix for text mode |
| `payload.format_mode` | string | No | `raw` | `raw` / `enhanced` / `strict` |
| `payload.use_plugins` | bool | No | `false` | Enable plugins |
| `payload.docintel_endpoint` | string \| null | No | `null` | Auto-enables docintel when non-empty |

**Request Body:**

```json
{
  "payload": {
    "text": "# Hello World",
    "suffix": ".md",
    "format_mode": "enhanced",
    "use_plugins": false,
    "docintel_endpoint": null
  }
}
```

---

#### Mode 2 — File Upload (`Content-Type: multipart/form-data`)

**Request Parameters**

| Field | Type | Required | Default | Constraints |
|---|---|---|---|---|
| `file` | File | No | — | If provided, file conversion is used; max 10MB |
| `text` | string | No | `null` | Text content (used when no file) |
| `suffix` | string | No | `.txt` | Temp file suffix for text mode |
| `format_mode` | string | No | `raw` | `raw` / `enhanced` / `strict` |
| `use_plugins` | bool | No | `false` | `true` / `false` |
| `docintel_endpoint` | string | No | — | Auto-enables docintel when non-empty |

**Request Body (file upload):**

```json
{
  "file": "<binary: document.pdf>",
  "format_mode": "enhanced",
  "use_plugins": false
}
```

**Request Body (text only):**

```json
{
  "text": "Hello World",
  "suffix": ".txt",
  "format_mode": "raw"
}
```

---

#### Response

```json
{
  "code": 0,
  "message": "markitdown executed",
  "data": {
    "tool": "markitdown",
    "source": "upload:document.pdf",
    "format_mode": "enhanced",
    "markdown": "# Title\n\nContent..."
  },
  "request_id": "uuid"
}
```

| Field | Type | Description |
|---|---|---|
| `data.tool` | string | Always `markitdown` |
| `data.source` | string | `inline-text` or `upload:<filename>` |
| `data.format_mode` | string | Effective format mode |
| `data.markdown` | string | Converted Markdown content |

---

## 3. Error Handling

| Scenario | HTTP Status | Code | Description |
|---|---|---|---|
| File larger than 10MB | `413` | `41300` | `Uploaded file is too large. Max size is 10MB.` |
| Invalid `format_mode` | `422` | — | FastAPI validation error |
| Unhandled runtime exception | `500` | `50000` | `Internal server error: ...` |

Error response envelope:

```json
{
  "code": 41300,
  "message": "Uploaded file is too large. Max size is 10MB.",
  "data": {},
  "request_id": "uuid"
}
```

---

## 4. Examples

### JSON Text Conversion (curl)

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

### File Upload Conversion (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -F "file=@document.pdf" \
  -F "format_mode=strict" \
  -F "use_plugins=false"
```

### Python Example

```python
import requests

url = "https://relax-api.onrender.com/api/v1/tools/markitdown/execute"

# JSON mode
resp = requests.post(url, json={
    "payload": {
        "text": "# Title",
        "format_mode": "enhanced",
        "use_plugins": False,
        "docintel_endpoint": None,
    }
}, timeout=60)
print(resp.json()["data"]["markdown"])

# File upload mode
with open("document.pdf", "rb") as f:
    resp = requests.post(url, files={"file": f}, data={"format_mode": "raw"}, timeout=60)
print(resp.json()["data"]["markdown"])
```

---

## 5. Limits and Notes

- `format_mode` only accepts: `raw`, `enhanced`, `strict`
- `docintel_endpoint` is only activated when the value is non-empty
- Provide at least one of `file` or `text`; if both are provided, `file` takes precedence
