# Image Toolkit API Documentation

## 1. Overview

The `image` service provides image processing capabilities through HTTP endpoints.

- **Base URL**: `https://relax-api.onrender.com`
- **Endpoints**:
  - `POST /api/v1/tools/image/compress` — Compress image
  - `POST /api/v1/tools/image/resize` — Resize image
  - `POST /api/v1/tools/image/convert` — Convert image format
  - `POST /api/v1/tools/image/watermark` — Add text watermark
- **Request type**: `multipart/form-data`
- **Upload limit**: 10MB per request

---

## 2. Endpoints

### `POST /api/v1/tools/image/compress` — Compress

**Description**: Compress an image with adjustable quality. Supported input formats: JPEG, PNG, WebP.

**Request Parameters**

| Field | Type | Required | Default | Constraints |
|---|---|---|---|---|
| `file` | File | Yes | — | Image file (JPEG/PNG/WebP) |
| `quality` | int | No | `80` | Quality 1–100 |

**Request Body:**

```json
{
  "file": "<binary: photo.jpg>",
  "quality": 70
}
```

**Response:**

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

| Field | Type | Description |
|---|---|---|
| `data.image` | string | Base64-encoded compressed image |
| `data.format` | string | Output format |
| `data.original_size` | int | Original file size in bytes |
| `data.compressed_size` | int | Compressed file size in bytes |
| `data.compression_ratio` | float | Compression ratio (0–1) |

---

### `POST /api/v1/tools/image/resize` — Resize

**Description**: Resize image with optional aspect ratio preservation.

**Request Parameters**

| Field | Type | Required | Default | Constraints |
|---|---|---|---|---|
| `file` | File | Yes | — | Image file |
| `width` | int | No | — | Target width in pixels |
| `height` | int | No | — | Target height in pixels |
| `fit` | string | No | `inside` | `inside` / `outside` / `cover` / `contain` |

> At least one of `width` or `height` is required.

**Fit modes:**

| Value | Description |
|---|---|
| `inside` | Scale down proportionally to fit within bounds |
| `outside` | Scale up proportionally to cover bounds |
| `cover` | Crop to fill the target dimensions exactly |
| `contain` | Scale proportionally with letterboxing |

**Request Body:**

```json
{
  "file": "<binary: photo.jpg>",
  "width": 800,
  "height": 600,
  "fit": "inside"
}
```

**Response:**

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

---

### `POST /api/v1/tools/image/convert` — Convert Format

**Description**: Convert image to a different format. Supported output formats: `webp`, `jpeg`, `png`, `avif`.

**Request Parameters**

| Field | Type | Required | Constraints |
|---|---|---|---|
| `file` | File | Yes | Image file |
| `format` | string | Yes | `webp` / `jpeg` / `png` / `avif` |

**Request Body:**

```json
{
  "file": "<binary: photo.png>",
  "format": "webp"
}
```

**Response:**

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

---

### `POST /api/v1/tools/image/watermark` — Add Watermark

**Description**: Add a text watermark to an image.

**Request Parameters**

| Field | Type | Required | Default | Constraints |
|---|---|---|---|---|
| `file` | File | Yes | — | Image file |
| `text` | string | Yes | — | Watermark text |
| `position` | string | No | `bottom-right` | `top-left` / `top-right` / `bottom-left` / `bottom-right` / `center` |

**Request Body:**

```json
{
  "file": "<binary: photo.jpg>",
  "text": "© 2026 MyBrand",
  "position": "bottom-right"
}
```

**Response:**

```json
{
  "code": 0,
  "message": "watermark added",
  "data": {
    "image": "base64...",
    "format": "png",
    "text": "© 2026 MyBrand",
    "position": "bottom-right"
  },
  "request_id": "uuid"
}
```

---

## 3. Error Handling

| Scenario | HTTP Status | Code | Description |
|---|---|---|---|
| File larger than 10MB | `413` | `41300` | `Uploaded file is too large. Max size is 10MB.` |
| Invalid format value | `422` | — | FastAPI validation error |
| Processing error | `500` | `50000` | Internal server error |

---

## 4. Examples

### Compress (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/compress" \
  -F "file=@photo.jpg" \
  -F "quality=70"
```

### Resize (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/resize" \
  -F "file=@photo.jpg" \
  -F "width=800" \
  -F "height=600" \
  -F "fit=inside"
```

### Convert to WebP (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/convert" \
  -F "file=@photo.png" \
  -F "format=webp"
```

### Add Watermark (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/watermark" \
  -F "file=@photo.jpg" \
  -F "text=© 2026 MyBrand" \
  -F "position=bottom-right"
```

### Python Example

```python
import requests, base64

BASE_URL = "https://relax-api.onrender.com/api/v1/tools/image"

with open("photo.jpg", "rb") as f:
    resp = requests.post(f"{BASE_URL}/compress", files={"file": f}, data={"quality": 70})
result = resp.json()

img_data = base64.b64decode(result["data"]["image"])
with open("compressed.jpg", "wb") as f:
    f.write(img_data)
print(f"Compression ratio: {result['data']['compression_ratio']}")
```

---

## 5. Limits and Notes

- Maximum file size: **10MB**
- Supported input formats: JPEG, PNG, WebP, AVIF, GIF, BMP, TIFF
- Output image is returned as **Base64-encoded** string in JSON response
- Watermark uses semi-transparent black background with white text
- AVIF support depends on PIL/Pillow version and system libraries
