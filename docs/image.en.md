# Image Toolkit API Documentation

## 1. Overview

The `image` service provides image processing capabilities including compression, resizing, format conversion, and watermarking through HTTP endpoints.

- **Base URL**: `https://relax-api.onrender.com`
- **Endpoints**:
  - `POST /api/v1/tools/image/compress` - Compress image
  - `POST /api/v1/tools/image/resize` - Resize image
  - `POST /api/v1/tools/image/convert` - Convert image format
  - `POST /api/v1/tools/image/watermark` - Add text watermark
- **Request type**: `multipart/form-data`

## 2. Endpoints

### 2.1 Compress Image

- **Method**: `POST`
- **Path**: `/api/v1/tools/image/compress`
- **Description**: Compress an image with adjustable quality
- **Supported formats**: JPEG, PNG, WebP

### 2.2 Resize Image

- **Method**: `POST`
- **Path**: `/api/v1/tools/image/resize`
- **Description**: Resize image with optional aspect ratio preservation
- **Fit modes**: `inside`, `outside`, `cover`, `contain`

### 2.3 Convert Image Format

- **Method**: `POST`
- **Path**: `/api/v1/tools/image/convert`
- **Description**: Convert image to different format
- **Supported output formats**: `webp`, `jpeg`, `png`, `avif`

### 2.4 Add Watermark

- **Method**: `POST`
- **Path**: `/api/v1/tools/image/watermark`
- **Description**: Add text watermark to image
- **Positions**: `top-left`, `top-right`, `bottom-left`, `bottom-right`, `center`

## 3. Request Parameters

### 3.1 Compress Image

| Field | Type | Required | Default | Constraints |
|---|---|---:|---|---|
| `file` | File | Yes | - | Image file (JPEG/PNG/WebP) |
| `quality` | int | No | `80` | Range: 1-100 |

Upload limit: **10MB**

### 3.2 Resize Image

| Field | Type | Required | Default | Constraints |
|---|---|---:|---|---|
| `file` | File | Yes | - | Image file |
| `width` | int | No | - | Target width in pixels |
| `height` | int | No | - | Target height in pixels |
| `fit` | string | No | `inside` | `inside` / `outside` / `cover` / `contain` |

**Fit modes**:
- `inside`: Preserves aspect ratio, fits within dimensions
- `outside`: Preserves aspect ratio, covers dimensions
- `cover`: Forces exact dimensions (may distort)
- `contain`: Same as inside

### 3.3 Convert Image Format

| Field | Type | Required | Default | Constraints |
|---|---|---:|---|---|
| `file` | File | Yes | - | Image file |
| `format` | string | Yes | - | `webp` / `jpeg` / `png` / `avif` |

### 3.4 Add Watermark

| Field | Type | Required | Default | Constraints |
|---|---|---:|---|---|
| `file` | File | Yes | - | Image file |
| `text` | string | Yes | - | Watermark text |
| `position` | string | No | `bottom-right` | `top-left` / `top-right` / `bottom-left` / `bottom-right` / `center` |

## 4. Response Schema

Success response (unified envelope):

```json
{
  "code": 0,
  "message": "image compressed",
  "data": {
    "image": "base64_encoded_string",
    "format": "jpeg",
    "...": "additional fields vary by endpoint"
  },
  "request_id": "uuid"
}
```

### 4.1 Compress Response

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

### 4.2 Resize Response

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

### 4.3 Convert Response

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

### 4.4 Watermark Response

```json
{
  "code": 0,
  "message": "watermark added",
  "data": {
    "image": "base64...",
    "format": "png",
    "text": "© 2026",
    "position": "bottom-right"
  },
  "request_id": "uuid"
}
```

## 5. Error Handling

| Scenario | HTTP Status | Business Code | Description |
|---|---:|---:|---|
| File larger than 10MB | `413` | `41300` | `Uploaded file is too large. Max size is 10MB.` |
| Invalid format | `422` | - | FastAPI validation error |
| Unsupported format | `500` | `50000` | Internal processing error |

## 6. Examples

### 6.1 Compress Image (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/compress" \
  -F "file=@photo.jpg" \
  -F "quality=70"
```

### 6.2 Resize Image (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/resize" \
  -F "file=@photo.jpg" \
  -F "width=800" \
  -F "height=600" \
  -F "fit=inside"
```

### 6.3 Convert to WebP (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/convert" \
  -F "file=@photo.png" \
  -F "format=webp"
```

### 6.4 Add Watermark (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/watermark" \
  -F "file=@photo.jpg" \
  -F "text=© 2026 MyBrand" \
  -F "position=bottom-right"
```

### 6.5 Python Example

```python
import requests
import base64

BASE_URL = "https://relax-api.onrender.com/api/v1/tools/image"

# Compress
with open("photo.jpg", "rb") as f:
    resp = requests.post(
        f"{BASE_URL}/compress",
        files={"file": f},
        data={"quality": 70}
    )
result = resp.json()
print(f"Compression ratio: {result['data']['compression_ratio']}")

# Save result
img_data = base64.b64decode(result["data"]["image"])
with open("compressed.jpg", "wb") as f:
    f.write(img_data)
```

## 7. Limits and Notes

- Maximum file size: **10MB**
- Supported input formats: JPEG, PNG, WebP, AVIF, GIF, BMP, TIFF
- Output image is returned as **base64-encoded** string in JSON response
- Watermark uses semi-transparent black background with white text
- AVIF support depends on PIL/Pillow version and system libraries
