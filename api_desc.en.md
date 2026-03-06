# relax-api API Documentation

**Base URL**: `https://relax-api.onrender.com`

---

## Table of Contents

- [General](#general)
- [Health Check](#health-check)
- [markitdown — Convert to Markdown](#markitdown--convert-to-markdown)
- [image — Image Processing](#image--image-processing)
- [qrcode — QR Code](#qrcode--qr-code)

---

## General

### Response Schema

All endpoints return a unified JSON structure:

```json
{
  "code": 0,
  "message": "ok",
  "data": { ... },
  "request_id": "abc123"
}
```

| Field | Type | Description |
|---|---|---|
| `code` | int | `0` = success, non-zero = error |
| `message` | string | Result description |
| `data` | object | Business data |
| `request_id` | string | Unique request ID |

### Error Codes

| HTTP Status | code | Meaning |
|---|---|---|
| 400 | 40000 | Bad request |
| 413 | 41300 | File too large (max 10MB) |
| 422 | 42200 | Validation error |
| 500 | 50000 | Internal server error |

---

## Health Check

### `GET /healthz`

Liveness probe. Returns 200 when the service is alive.

**Sample URL:**

```
GET https://relax-api.onrender.com/healthz
```

### `GET /readyz`

Readiness probe. Returns 200 when the service is ready.

**Sample URL:**

```
GET https://relax-api.onrender.com/readyz
```

---

## markitdown — Convert to Markdown

Convert text or files to Markdown format. Supports PDF, Word, PPT, Excel, and more.

### `POST /api/v1/tools/markitdown/execute`

**Content-Type**: `multipart/form-data` or `application/json`

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `file` | file | No | — | Uploaded file (multipart) |
| `text` | string | No | — | Inline text content |
| `suffix` | string | No | `.txt` | Temp file suffix for inline text mode |
| `format_mode` | string | No | `raw` | Markdown post-process mode: `raw` / `enhanced` / `strict` |
| `use_plugins` | bool | No | `false` | Enable plugins |
| `docintel_endpoint` | string | No | — | Document Intelligence endpoint; enables docintel mode when provided |

> At least one of `file` or `text` is required. Max file size: 10MB.

**Request Body (file upload — multipart/form-data):**

```json
{
  "file": "<binary: document.pdf>",
  "format_mode": "enhanced",
  "use_plugins": false
}
```

**Request Body (text only — multipart/form-data):**

```json
{
  "text": "Hello World",
  "suffix": ".txt",
  "format_mode": "raw"
}
```

**Request Body (JSON mode — application/json):**

```json
{
  "payload": {
    "text": "Hello World",
    "suffix": ".txt",
    "format_mode": "enhanced",
    "use_plugins": false,
    "docintel_endpoint": null
  }
}
```

#### Response Data

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
  "request_id": "abc123"
}
```

#### Examples

```bash
# Upload a file
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -F "file=@document.pdf"

# Convert inline text
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -F "text=Hello World" \
  -F "suffix=.txt"

# JSON request
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -H "Content-Type: application/json" \
  -d '{"payload": {"text": "Hello World", "format_mode": "enhanced"}}'
```

---

## image — Image Processing

A toolkit for image compression, resizing, format conversion, and text watermarking. Max file size: 10MB.

### `POST /api/v1/tools/image/compress` — Compress

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `file` | file | Yes | — | Image file (JPEG/PNG/WebP) |
| `quality` | int | No | `80` | Compression quality 1–100 |

**Request Body:**

```json
{
  "file": "<binary: photo.jpg>",
  "quality": 70
}
```

#### Response Data

```json
{
  "code": 0,
  "message": "image compressed",
  "data": {
    "image": "base64...",
    "format": "jpeg",
    "original_size": 1024000,
    "compressed_size": 512000,
    "compression_ratio": 0.5
  },
  "request_id": "uuid"
}
```

#### Example

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/compress" \
  -F "file=@photo.jpg" \
  -F "quality=70"
```

---

### `POST /api/v1/tools/image/resize` — Resize

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `file` | file | Yes | — | Image file |
| `width` | int | No | — | Target width (px) |
| `height` | int | No | — | Target height (px) |
| `fit` | string | No | `inside` | Fit mode: `inside` / `outside` / `cover` / `contain` |

> At least one of `width` or `height` is required.

**Request Body:**

```json
{
  "file": "<binary: photo.jpg>",
  "width": 800,
  "height": 600,
  "fit": "inside"
}
```

**Fit modes:**

| Value | Description |
|---|---|
| `inside` | Scale down proportionally to fit within bounds |
| `outside` | Scale up proportionally to cover bounds |
| `cover` | Crop to fill the target dimensions exactly |
| `contain` | Scale proportionally with letterboxing |

#### Response Data

```json
{
  "code": 0,
  "message": "image resized",
  "data": {
    "image": "base64...",
    "format": "jpeg",
    "original_size": {"width": 1920, "height": 1080},
    "new_size": {"width": 800, "height": 450}
  },
  "request_id": "uuid"
}
```

#### Example

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/resize" \
  -F "file=@photo.jpg" \
  -F "width=800" \
  -F "fit=inside"
```

---

### `POST /api/v1/tools/image/convert` — Convert Format

#### Request Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `file` | file | Yes | Image file |
| `format` | string | Yes | Target format: `webp` / `jpeg` / `png` / `avif` |

**Request Body:**

```json
{
  "file": "<binary: photo.png>",
  "format": "webp"
}
```

#### Response Data

```json
{
  "code": 0,
  "message": "image converted",
  "data": {
    "image": "base64...",
    "format": "webp",
    "mime_type": "image/webp"
  },
  "request_id": "uuid"
}
```

#### Example

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/convert" \
  -F "file=@photo.png" \
  -F "format=webp"
```

---

### `POST /api/v1/tools/image/watermark` — Text Watermark

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `file` | file | Yes | — | Image file |
| `text` | string | Yes | — | Watermark text |
| `position` | string | No | `bottom-right` | Position: `top-left` / `top-right` / `bottom-left` / `bottom-right` / `center` |

**Request Body:**

```json
{
  "file": "<binary: photo.jpg>",
  "text": "© 2025 My Brand",
  "position": "bottom-right"
}
```

#### Response Data

```json
{
  "code": 0,
  "message": "watermark added",
  "data": {
    "image": "base64...",
    "format": "png",
    "text": "© 2025 My Brand",
    "position": "bottom-right"
  },
  "request_id": "uuid"
}
```

#### Example

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/watermark" \
  -F "file=@photo.jpg" \
  -F "text=© 2025 My Brand" \
  -F "position=bottom-right"
```

---

## qrcode — QR Code

QR code generation and decoding tool. Max file size: 10MB.

### `GET /api/v1/tools/qrcode/generate` — Generate

#### Request Parameters (Query String)

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `text` | string | Yes | — | QR code content |
| `size` | int | No | `300` | Image size in px (100–1000) |
| `format` | string | No | `png` | Output format: `png` / `jpeg` / `webp` |

**Sample URL:**

```
GET https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com&size=300&format=png
```

#### Response Data

```json
{
  "code": 0,
  "message": "qrcode generated",
  "data": {
    "image": "base64...",
    "format": "png",
    "mime_type": "image/png",
    "text": "https://example.com",
    "size": 300
  },
  "request_id": "uuid"
}
```

---

### `POST /api/v1/tools/qrcode/decode` — Decode

#### Request Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `file` | file | Yes | Image containing the QR code |

**Request Body:**

```json
{
  "file": "<binary: qrcode.png>"
}
```

#### Response Data

```json
{
  "code": 0,
  "message": "qrcode decoded",
  "data": {
    "results": [
      {"type": "QRCODE", "data": "https://example.com"}
    ],
    "count": 1
  },
  "request_id": "uuid"
}
```

#### Example

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/qrcode/decode" \
  -F "file=@qrcode.png"
```
