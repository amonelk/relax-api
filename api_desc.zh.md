# relax-api 接口说明

**线上地址**：`https://relax-api.onrender.com`

---

## 目录

- [通用规范](#通用规范)
- [健康检查](#健康检查)
- [markitdown — 文档转 Markdown](#markitdown--文档转-markdown)
- [image — 图片处理](#image--图片处理)
- [qrcode — 二维码](#qrcode--二维码)

---

## 通用规范

### 响应结构

所有接口均返回统一 JSON 结构：

```json
{
  "code": 0,
  "message": "ok",
  "data": { ... },
  "request_id": "abc123"
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | int | `0` 表示成功，非 0 表示错误 |
| `message` | string | 结果描述 |
| `data` | object | 业务数据 |
| `request_id` | string | 请求唯一 ID |

### 错误码

| HTTP 状态码 | code | 含义 |
|---|---|---|
| 400 | 40000 | 参数错误 |
| 413 | 41300 | 文件过大（上限 10MB） |
| 422 | 42200 | 参数校验失败 |
| 500 | 50000 | 服务内部错误 |

---

## 健康检查

### `GET /healthz`

活性探针，服务存活时返回 200。

**请求样例 URL：**

```
GET https://relax-api.onrender.com/healthz
```

### `GET /readyz`

就绪探针，服务就绪时返回 200。

**请求样例 URL：**

```
GET https://relax-api.onrender.com/readyz
```

---

## markitdown — 文档转 Markdown

将文本或文件转换为 Markdown 格式，支持 PDF、Word、PPT、Excel 等常见文档格式。

### `POST /api/v1/tools/markitdown/execute`

**Content-Type**：`multipart/form-data` 或 `application/json`

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `file` | file | 否 | — | 上传文件（multipart） |
| `text` | string | 否 | — | 内联文本内容 |
| `suffix` | string | 否 | `.txt` | 内联文本模式下的临时文件后缀 |
| `format_mode` | string | 否 | `raw` | Markdown 后处理模式：`raw` / `enhanced` / `strict` |
| `use_plugins` | bool | 否 | `false` | 是否启用插件 |
| `docintel_endpoint` | string | 否 | — | Document Intelligence 端点，提供后自动启用 docintel 模式 |

> `file` 与 `text` 至少提供一个。文件大小上限 10MB。

**请求体（文件上传 — multipart/form-data）：**

```json
{
  "file": "<binary: document.pdf>",
  "format_mode": "enhanced",
  "use_plugins": false
}
```

**请求体（纯文本 — multipart/form-data）：**

```json
{
  "text": "Hello World",
  "suffix": ".txt",
  "format_mode": "raw"
}
```

**请求体（JSON 模式 — application/json）：**

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

#### 返回数据

```json
{
  "code": 0,
  "message": "markitdown executed",
  "data": {
    "tool": "markitdown",
    "source": "upload:document.pdf",
    "format_mode": "enhanced",
    "markdown": "# 标题\n\n内容..."
  },
  "request_id": "abc123"
}
```

#### 示例

```bash
# 上传文件
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -F "file=@document.pdf"

# 转换内联文本
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -F "text=Hello World" \
  -F "suffix=.txt"

# JSON 请求
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -H "Content-Type: application/json" \
  -d '{"payload": {"text": "Hello World", "format_mode": "enhanced"}}'
```

---

## image — 图片处理

图片处理工具集，支持压缩、缩放、格式转换和添加文字水印。文件大小上限 10MB。

### `POST /api/v1/tools/image/compress` — 压缩

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `file` | file | 是 | — | 图片文件（JPEG/PNG/WebP） |
| `quality` | int | 否 | `80` | 压缩质量 1–100 |

**请求体：**

```json
{
  "file": "<binary: photo.jpg>",
  "quality": 70
}
```

#### 返回数据

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

#### 示例

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/compress" \
  -F "file=@photo.jpg" \
  -F "quality=70"
```

---

### `POST /api/v1/tools/image/resize` — 缩放

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `file` | file | 是 | — | 图片文件 |
| `width` | int | 否 | — | 目标宽度（px） |
| `height` | int | 否 | — | 目标高度（px） |
| `fit` | string | 否 | `inside` | 缩放模式：`inside` / `outside` / `cover` / `contain` |

> `width` 与 `height` 至少提供一个。

**请求体：**

```json
{
  "file": "<binary: photo.jpg>",
  "width": 800,
  "height": 600,
  "fit": "inside"
}
```

**fit 模式说明：**

| 值 | 说明 |
|---|---|
| `inside` | 等比缩小，尺寸不超过目标 |
| `outside` | 等比放大，尺寸不小于目标 |
| `cover` | 裁剪填满目标尺寸 |
| `contain` | 等比缩放并留白 |

#### 返回数据

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

#### 示例

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/resize" \
  -F "file=@photo.jpg" \
  -F "width=800" \
  -F "fit=inside"
```

---

### `POST /api/v1/tools/image/convert` — 格式转换

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | file | 是 | 图片文件 |
| `format` | string | 是 | 目标格式：`webp` / `jpeg` / `png` / `avif` |

**请求体：**

```json
{
  "file": "<binary: photo.png>",
  "format": "webp"
}
```

#### 返回数据

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

#### 示例

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/convert" \
  -F "file=@photo.png" \
  -F "format=webp"
```

---

### `POST /api/v1/tools/image/watermark` — 文字水印

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `file` | file | 是 | — | 图片文件 |
| `text` | string | 是 | — | 水印文字 |
| `position` | string | 否 | `bottom-right` | 位置：`top-left` / `top-right` / `bottom-left` / `bottom-right` / `center` |

**请求体：**

```json
{
  "file": "<binary: photo.jpg>",
  "text": "© 2025 My Brand",
  "position": "bottom-right"
}
```

#### 返回数据

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

#### 示例

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/watermark" \
  -F "file=@photo.jpg" \
  -F "text=© 2025 My Brand" \
  -F "position=bottom-right"
```

---

## qrcode — 二维码

二维码生成与解析工具。文件大小上限 10MB。

### `GET /api/v1/tools/qrcode/generate` — 生成

#### 请求参数（Query String）

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `text` | string | 是 | — | 二维码内容 |
| `size` | int | 否 | `300` | 图片尺寸 px（100–1000） |
| `format` | string | 否 | `png` | 输出格式：`png` / `jpeg` / `webp` |

**请求样例 URL：**

```
GET https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com&size=300&format=png
```

#### 返回数据

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

### `POST /api/v1/tools/qrcode/decode` — 解析

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | file | 是 | 包含二维码的图片 |

**请求体：**

```json
{
  "file": "<binary: qrcode.png>"
}
```

#### 返回数据

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

#### 示例

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/qrcode/decode" \
  -F "file=@qrcode.png"
```
