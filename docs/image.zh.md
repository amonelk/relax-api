# Image Toolkit API 文档

## 1. 概述

`image` 服务提供图片处理能力，包括压缩、调整尺寸、格式转换和添加水印，通过 HTTP 接口提供能力。

- **Base URL**：`https://relax-api.onrender.com`
- **接口列表**：
  - `POST /api/v1/tools/image/compress` - 压缩图片
  - `POST /api/v1/tools/image/resize` - 调整尺寸
  - `POST /api/v1/tools/image/convert` - 格式转换
  - `POST /api/v1/tools/image/watermark` - 添加水印
- **请求方式**：`multipart/form-data`

## 2. 接口详情

### 2.1 压缩图片

- **Method**: `POST`
- **Path**: `/api/v1/tools/image/compress`
- **描述**：压缩图片，可调节压缩质量
- **支持格式**：JPEG、PNG、WebP

### 2.2 调整尺寸

- **Method**: `POST`
- **Path**: `/api/v1/tools/image/resize`
- **描述**：调整图片尺寸，支持保持宽高比
- **缩放模式**：`inside`、`outside`、`cover`、`contain`

### 2.3 格式转换

- **Method**: `POST`
- **Path**: `/api/v1/tools/image/convert`
- **描述**：转换图片格式
- **支持输出格式**：`webp`、`jpeg`、`png`、`avif`

### 2.4 添加水印

- **Method**: `POST`
- **Path**: `/api/v1/tools/image/watermark`
- **描述**：为图片添加文字水印
- **位置选项**：`top-left`、`top-right`、`bottom-left`、`bottom-right`、`center`

## 3. 请求参数

### 3.1 压缩图片

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---:|---|---|
| `file` | File | 是 | - | 图片文件（JPEG/PNG/WebP） |
| `quality` | int | 否 | `80` | 范围：1-100 |

上传限制：**10MB**

### 3.2 调整尺寸

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---:|---|---|
| `file` | File | 是 | - | 图片文件 |
| `width` | int | 否 | - | 目标宽度（像素） |
| `height` | int | 否 | - | 目标高度（像素） |
| `fit` | string | 否 | `inside` | `inside` / `outside` / `cover` / `contain` |

**缩放模式说明**：
- `inside`：保持宽高比，图片完全在指定尺寸内
- `outside`：保持宽高比，图片覆盖指定尺寸
- `cover`：强制拉伸到指定尺寸（可能变形）
- `contain`：同 inside

### 3.3 格式转换

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---:|---|---|
| `file` | File | 是 | - | 图片文件 |
| `format` | string | 是 | - | `webp` / `jpeg` / `png` / `avif` |

### 3.4 添加水印

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---:|---|---|
| `file` | File | 是 | - | 图片文件 |
| `text` | string | 是 | - | 水印文字 |
| `position` | string | 否 | `bottom-right` | `top-left` / `top-right` / `bottom-left` / `bottom-right` / `center` |

## 4. 返回结构

成功返回（统一格式）：

```json
{
  "code": 0,
  "message": "image compressed",
  "data": {
    "image": "base64编码字符串",
    "format": "jpeg",
    "...": "其他字段因接口而异"
  },
  "request_id": "uuid"
}
```

### 4.1 压缩返回

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
| `data.image` | string | Base64 编码的图片数据 |
| `data.format` | string | 输出格式 |
| `data.original_size` | int | 原始文件大小（字节） |
| `data.compressed_size` | int | 压缩后大小（字节） |
| `data.compression_ratio` | float | 压缩比例（0-1） |

### 4.2 调整尺寸返回

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

### 4.3 格式转换返回

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

### 4.4 水印返回

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

## 5. 错误处理

| 场景 | HTTP 状态码 | 业务码 | 说明 |
|---|---:|---:|---|
| 文件超过 10MB | `413` | `41300` | `Uploaded file is too large. Max size is 10MB.` |
| 参数校验失败 | `422` | - | FastAPI 校验错误结构 |
| 处理异常 | `500` | `50000` | `Internal server error: ...` |

## 6. 示例

### 6.1 压缩图片（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/compress" \
  -F "file=@photo.jpg" \
  -F "quality=70"
```

### 6.2 调整尺寸（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/resize" \
  -F "file=@photo.jpg" \
  -F "width=800" \
  -F "height=600" \
  -F "fit=inside"
```

### 6.3 转换为 WebP（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/convert" \
  -F "file=@photo.png" \
  -F "format=webp"
```

### 6.4 添加水印（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/watermark" \
  -F "file=@photo.jpg" \
  -F "text=© 2026 我的作品" \
  -F "position=bottom-right"
```

### 6.5 Python 调用

```python
import requests
import base64

BASE_URL = "https://relax-api.onrender.com/api/v1/tools/image"

# 压缩图片
with open("photo.jpg", "rb") as f:
    resp = requests.post(
        f"{BASE_URL}/compress",
        files={"file": f},
        data={"quality": 70}
    )
result = resp.json()
print(f"压缩比例: {result['data']['compression_ratio']}")

# 保存结果
img_data = base64.b64decode(result["data"]["image"])
with open("compressed.jpg", "wb") as f:
    f.write(img_data)
```

## 7. 限制与注意事项

- 最大文件大小：**10MB**
- 支持输入格式：JPEG、PNG、WebP、AVIF、GIF、BMP、TIFF
- 输出图片以 **Base64 编码** 返回在 JSON 响应中
- 水印使用半透明黑色背景 + 白色文字
- AVIF 支持取决于 PIL/Pillow 版本和系统库
