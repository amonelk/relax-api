# QR Code Toolkit API Documentation

## 1. Overview

The `qrcode` service provides QR code generation and decoding capabilities through HTTP endpoints.

- **Base URL**: `https://relax-api.onrender.com`
- **Endpoints**:
  - `GET /api/v1/tools/qrcode/generate` - Generate QR code
  - `POST /api/v1/tools/qrcode/decode` - Decode QR code from image
- **Request types**:
  - `GET` with query parameters (generate)
  - `multipart/form-data` (decode)

## 2. Endpoints

### 2.1 Generate QR Code

- **Method**: `GET`
- **Path**: `/api/v1/tools/qrcode/generate`
- **Description**: Generate a QR code image from text content
- **Output formats**: PNG, JPEG, WebP

### 2.2 Decode QR Code

- **Method**: `POST`
- **Path**: `/api/v1/tools/qrcode/decode`
- **Description**: Extract QR code content from an image
- **Note**: Requires `pyzbar` library with system `libzbar` dependency

## 3. Request Parameters

### 3.1 Generate QR Code

Query parameters:

| Field | Type | Required | Default | Constraints |
|---|---|---:|---|---|
| `text` | string | Yes | - | Content to encode (URL-encode if needed) |
| `size` | int | No | `300` | Image size in pixels (100-1000) |
| `format` | string | No | `png` | `png` / `jpeg` / `webp` |

### 3.2 Decode QR Code

Form fields:

| Field | Type | Required | Default | Constraints |
|---|---|---:|---|---|
| `file` | File | Yes | - | Image containing QR code |

Upload limit: **10MB**

## 4. Response Schema

### 4.1 Generate Response

```json
{
  "code": 0,
  "message": "qrcode generated",
  "data": {
    "image": "base64_encoded_string",
    "format": "png",
    "mime_type": "image/png",
    "text": "https://example.com",
    "size": 300
  },
  "request_id": "uuid"
}
```

Field details:

| Field | Type | Description |
|---|---|---|
| `data.image` | string | Base64-encoded QR code image |
| `data.format` | string | Output format |
| `data.mime_type` | string | MIME type for the image |
| `data.text` | string | Original encoded content |
| `data.size` | int | Image size in pixels |

### 4.2 Decode Response

Success (QR code found):

```json
{
  "code": 0,
  "message": "qrcode decoded",
  "data": {
    "results": [
      {
        "type": "QRCODE",
        "data": "https://example.com"
      }
    ],
    "count": 1
  },
  "request_id": "uuid"
}
```

No QR code detected:

```json
{
  "code": 0,
  "message": "qrcode decoded",
  "data": {
    "error": "No QR code detected",
    "results": []
  },
  "request_id": "uuid"
}
```

Feature unavailable (pyzbar not installed):

```json
{
  "code": 0,
  "message": "qrcode decoded",
  "data": {
    "error": "pyzbar not installed, decode feature unavailable",
    "results": []
  },
  "request_id": "uuid"
}
```

## 5. Error Handling

| Scenario | HTTP Status | Business Code | Description |
|---|---:|---:|---|
| File larger than 10MB | `413` | `41300` | `Uploaded file is too large. Max size is 10MB.` |
| Missing required parameter | `422` | - | FastAPI validation error |
| Processing error | `500` | `50000` | Internal server error |

## 6. Examples

### 6.1 Generate QR Code (curl)

Basic usage:
```bash
curl "https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com"
```

With custom size and format:
```bash
curl "https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com&size=500&format=webp"
```

URL with special characters (URL-encoded):
```bash
curl "https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https%3A%2F%2Fexample.com%2Fpath%3Fid%3D123"
```

### 6.2 Decode QR Code (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/qrcode/decode" \
  -F "file=@qrcode.png"
```

### 6.3 Python Example

```python
import requests
import base64

BASE_URL = "https://relax-api.onrender.com/api/v1/tools/qrcode"

# Generate QR code
resp = requests.get(
    f"{BASE_URL}/generate",
    params={
        "text": "https://example.com",
        "size": 400,
        "format": "png"
    }
)
result = resp.json()

# Save QR code image
img_data = base64.b64decode(result["data"]["image"])
with open("qrcode.png", "wb") as f:
    f.write(img_data)
print(f"QR code saved: {result['data']['text']}")

# Decode QR code
with open("qrcode.png", "rb") as f:
    resp = requests.post(
        f"{BASE_URL}/decode",
        files={"file": f}
    )
result = resp.json()
if result["data"]["results"]:
    print(f"Decoded: {result['data']['results'][0]['data']}")
else:
    print(f"Error: {result['data'].get('error', 'Unknown')}")
```

### 6.4 JavaScript Example

```javascript
// Generate QR code
const text = encodeURIComponent("https://example.com");
const url = `https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=${text}&size=300`;

fetch(url)
  .then(res => res.json())
  .then(data => {
    const img = document.createElement('img');
    img.src = `data:${data.data.mime_type};base64,${data.data.image}`;
    document.body.appendChild(img);
  });

// Decode QR code
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('https://relax-api.onrender.com/api/v1/tools/qrcode/decode', {
  method: 'POST',
  body: formData
})
  .then(res => res.json())
  .then(data => console.log(data.data.results));
```

## 7. Limits and Notes

- **Maximum file size**: 10MB for decode endpoint
- **QR code size**: 100-1000 pixels for generation
- **Decode feature**: Requires `pyzbar` library with system `libzbar` dependency
  - May not work on all hosting platforms (e.g., Render free tier)
  - Check `data.error` field in response for availability
- **Multiple QR codes**: Decode endpoint can detect multiple QR codes in a single image
- **Text encoding**: For URLs with special characters, use URL encoding
- **Error correction**: Generated QR codes use medium error correction level (M)
