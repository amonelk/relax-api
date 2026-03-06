# Image Toolkit API 文档

## 1. 概述

`image` 服务提供图片处理能力，通过 HTTP 接口提供。

- **Base URL**：`https://relax-api.onrender.com`
- **接口列表**：
  - `POST /api/v1/tools/image/compress` — 压缩图片
  - `POST /api/v1/tools/image/resize` — 调整尺寸
  - `POST /api/v1/tools/image/convert` — 格式转换
  - `POST /api/v1/tools/image/watermark` — 添加水印
- **请求方式**：`multipart/form-data`
- **文件大小上限**：每次请求 10MB

---

## 2. 接口详情

### `POST /api/v1/tools/image/compress` — 压缩

**描述**：压缩图片，可调节压缩质量。支持输入格式：JPEG、PNG、WebP。

**请求参数**

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---|---|---|
| `file` | File | 是 | — | 图片文件（JPEG/PNG/WebP） |
| `quality` | int | 否 | `80` | 质量 1–100 |

**请求体：**

```json
{
  "file": "<binary: photo.jpg>",
  "quality": 70
}
```

**返回：**

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

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.image` | string | Base64 编码的压缩后图片 |
| `data.format` | string | 输出格式 |
| `data.original_size` | int | 原始文件大小（字节） |
| `data.compressed_size` | int | 压缩后大小（字节） |
| `data.compression_ratio` | float | 压缩比例（0–1） |

---

### `POST /api/v1/tools/image/resize` — 调整尺寸

**描述**：调整图片尺寸，支持保持宽高比。

**请求参数**

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---|---|---|
| `file` | File | 是 | — | 图片文件 |
| `width` | int | 否 | — | 目标宽度（像素） |
| `height` | int | 否 | — | 目标高度（像素） |
| `fit` | string | 否 | `inside` | `inside` / `outside` / `cover` / `contain` |

> `width` 与 `height` 至少提供一个。

**缩放模式说明：**

| 值 | 说明 |
|---|---|
| `inside` | 等比缩小，尺寸不超过目标 |
| `outside` | 等比放大，尺寸不小于目标 |
| `cover` | 裁剪填满目标尺寸 |
| `contain` | 等比缩放并留白 |

**请求体：**

```json
{
  "file": "<binary: photo.jpg>",
  "width": 800,
  "height": 600,
  "fit": "inside"
}
```

**返回：**

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

### `POST /api/v1/tools/image/convert` — 格式转换

**描述**：转换图片格式。支持输出格式：`webp`、`jpeg`、`png`、`avif`。

**请求参数**

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `file` | File | 是 | 图片文件 |
| `format` | string | 是 | `webp` / `jpeg` / `png` / `avif` |

**请求体：**

```json
{
  "file": "<binary: photo.png>",
  "format": "webp"
}
```

**返回：**

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

### `POST /api/v1/tools/image/watermark` — 添加水印

**描述**：为图片添加文字水印。

**请求参数**

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---|---|---|
| `file` | File | 是 | — | 图片文件 |
| `text` | string | 是 | — | 水印文字 |
| `position` | string | 否 | `bottom-right` | `top-left` / `top-right` / `bottom-left` / `bottom-right` / `center` |

**请求体：**

```json
{
  "file": "<binary: photo.jpg>",
  "text": "© 2026 我的作品",
  "position": "bottom-right"
}
```

**返回：**

```json
{
  "code": 0,
  "message": "watermark added",
  "data": {
    "image": "base64...",
    "format": "png",
    "text": "© 2026 我的作品",
    "position": "bottom-right"
  },
  "request_id": "uuid"
}
```

---

## 3. 错误处理

| 场景 | HTTP 状态码 | 业务码 | 说明 |
|---|---|---|---|
| 文件超过 10MB | `413` | `41300` | `Uploaded file is too large. Max size is 10MB.` |
| 参数校验失败 | `422` | — | FastAPI 校验错误 |
| 处理异常 | `500` | `50000` | 内部服务器错误 |

---

## 4. 示例

### 压缩（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/compress" \
  -F "file=@photo.jpg" \
  -F "quality=70"
```

### 调整尺寸（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/resize" \
  -F "file=@photo.jpg" \
  -F "width=800" \
  -F "height=600" \
  -F "fit=inside"
```

### 转换为 WebP（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/convert" \
  -F "file=@photo.png" \
  -F "format=webp"
```

### 添加水印（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/watermark" \
  -F "file=@photo.jpg" \
  -F "text=© 2026 我的作品" \
  -F "position=bottom-right"
```

### Python 调用

```python
import requests, base64

BASE_URL = "https://relax-api.onrender.com/api/v1/tools/image"

with open("photo.jpg", "rb") as f:
    resp = requests.post(f"{BASE_URL}/compress", files={"file": f}, data={"quality": 70})
result = resp.json()

img_data = base64.b64decode(result["data"]["image"])
with open("compressed.jpg", "wb") as f:
    f.write(img_data)
print(f"压缩比例: {result['data']['compression_ratio']}")
```

---

## 5. 限制与注意事项

- 最大文件大小：**10MB**
- 支持输入格式：JPEG、PNG、WebP、AVIF、GIF、BMP、TIFF
- 输出图片以 **Base64 编码** 返回在 JSON 响应中
- 水印使用半透明黑色背景 + 白色文字
- AVIF 支持取决于 PIL/Pillow 版本和系统库
