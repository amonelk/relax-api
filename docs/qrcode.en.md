# QR Code Toolkit API Documentation

## 1. Overview

The `qrcode` service provides QR code generation and decoding through HTTP endpoints.

- **Base URL**: `https://relax-api.onrender.com`
- **Endpoints**:
  - `GET /api/v1/tools/qrcode/generate` — Generate QR code
  - `POST /api/v1/tools/qrcode/decode` — Decode QR code from image

---

## 2. Endpoints

### `GET /api/v1/tools/qrcode/generate` — Generate QR Code

**Description**: Generate a QR code image from text content. Output formats: PNG, JPEG, WebP.

**Request Parameters (Query String)**

| Field | Type | Required | Default | Constraints |
|---|---|---|---|---|
| `text` | string | Yes | — | Content to encode; URL-encode if it contains special characters |
| `size` | int | No | `300` | Image size in pixels (100–1000) |
| `format` | string | No | `png` | `png` / `jpeg` / `webp` |

**Sample Request URL:**

```
GET https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com&size=300&format=png
```

**Response:**

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

| Field | Type | Description |
|---|---|---|
| `data.image` | string | Base64-encoded QR code image |
| `data.format` | string | Output format |
| `data.mime_type` | string | MIME type of the image |
| `data.text` | string | Original encoded content |
| `data.size` | int | Image size in pixels |

---

### `POST /api/v1/tools/qrcode/decode` — Decode QR Code

**Description**: Extract QR code content from an uploaded image. Requires `pyzbar` with system `libzbar` dependency.

**Request Parameters (`multipart/form-data`)**

| Field | Type | Required | Constraints |
|---|---|---|---|
| `file` | File | Yes | Image containing QR code; max 10MB |

**Request Body:**

```json
{
  "file": "<binary: qrcode.png>"
}
```

**Response — QR code found:**

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

**Response — no QR code detected:**

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

**Response — decode feature unavailable (`pyzbar` not installed):**

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

---

## 3. Error Handling

| Scenario | HTTP Status | Code | Description |
|---|---|---|---|
| File larger than 10MB | `413` | `41300` | `Uploaded file is too large. Max size is 10MB.` |
| Missing required parameter | `422` | — | FastAPI validation error |
| Processing error | `500` | `50000` | Internal server error |

---

## 4. Examples

### Generate QR Code (curl)

```bash
# Basic
curl "https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com"

# Custom size and format
curl "https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com&size=500&format=webp"
```

### Decode QR Code (curl)

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/qrcode/decode" \
  -F "file=@qrcode.png"
```

### Python Example

```python
import requests, base64

BASE_URL = "https://relax-api.onrender.com/api/v1/tools/qrcode"

# Generate
resp = requests.get(f"{BASE_URL}/generate", params={"text": "https://example.com", "size": 400})
result = resp.json()
img_data = base64.b64decode(result["data"]["image"])
with open("qrcode.png", "wb") as f:
    f.write(img_data)

# Decode
with open("qrcode.png", "rb") as f:
    resp = requests.post(f"{BASE_URL}/decode", files={"file": f})
result = resp.json()
print(result["data"]["results"])
```

### JavaScript Example

```javascript
// Generate
const text = encodeURIComponent("https://example.com");
fetch(`https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=${text}&size=300`)
  .then(res => res.json())
  .then(data => {
    const img = document.createElement("img");
    img.src = `data:${data.data.mime_type};base64,${data.data.image}`;
    document.body.appendChild(img);
  });

// Decode
const formData = new FormData();
formData.append("file", fileInput.files[0]);
fetch("https://relax-api.onrender.com/api/v1/tools/qrcode/decode", { method: "POST", body: formData })
  .then(res => res.json())
  .then(data => console.log(data.data.results));
```

---

## 5. Limits and Notes

- Maximum file size for decode: **10MB**
- QR code size range for generate: **100–1000 pixels**
- Decode requires `pyzbar` library with system `libzbar`; check `data.error` if unavailable
- Multiple QR codes in a single image are all returned in `data.results`
- For URLs with special characters, apply URL encoding in query parameters
- Generated QR codes use medium error correction level (M)
