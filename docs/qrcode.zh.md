# QR Code Toolkit API 文档

## 1. 概述

`qrcode` 服务提供二维码生成和解析能力，通过 HTTP 接口提供。

- **Base URL**：`https://relax-api.onrender.com`
- **接口列表**：
  - `GET /api/v1/tools/qrcode/generate` — 生成二维码
  - `POST /api/v1/tools/qrcode/decode` — 解析二维码

---

## 2. 接口详情

### `GET /api/v1/tools/qrcode/generate` — 生成二维码

**描述**：根据文本内容生成二维码图片。支持输出格式：PNG、JPEG、WebP。

**请求参数（Query String）**

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---|---|---|
| `text` | string | 是 | — | 要编码的内容；含特殊字符需 URL 编码 |
| `size` | int | 否 | `300` | 图片尺寸（像素），范围 100–1000 |
| `format` | string | 否 | `png` | `png` / `jpeg` / `webp` |

**请求样例 URL：**

```
GET https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com&size=300&format=png
```

**返回：**

```json
{
  "code": 0,
  "message": "qrcode generated",
  "data": {
    "image": "base64编码字符串",
    "format": "png",
    "mime_type": "image/png",
    "text": "https://example.com",
    "size": 300
  },
  "request_id": "uuid"
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.image` | string | Base64 编码的二维码图片 |
| `data.format` | string | 输出格式 |
| `data.mime_type` | string | 图片 MIME 类型 |
| `data.text` | string | 原始编码内容 |
| `data.size` | int | 图片尺寸（像素） |

---

### `POST /api/v1/tools/qrcode/decode` — 解析二维码

**描述**：从上传图片中提取二维码内容。需要 `pyzbar` 库及系统 `libzbar` 依赖。

**请求参数（`multipart/form-data`）**

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `file` | File | 是 | 包含二维码的图片，最大 10MB |

**请求体：**

```json
{
  "file": "<binary: qrcode.png>"
}
```

**返回 — 成功检测到二维码：**

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

**返回 — 未检测到二维码：**

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

**返回 — 解析功能不可用（pyzbar 未安装）：**

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

## 3. 错误处理

| 场景 | HTTP 状态码 | 业务码 | 说明 |
|---|---|---|---|
| 文件超过 10MB | `413` | `41300` | `Uploaded file is too large. Max size is 10MB.` |
| 缺少必填参数 | `422` | — | FastAPI 校验错误 |
| 处理异常 | `500` | `50000` | 内部服务器错误 |

---

## 4. 示例

### 生成二维码（curl）

```bash
# 基本用法
curl "https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com"

# 自定义尺寸和格式
curl "https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com&size=500&format=webp"
```

### 解析二维码（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/qrcode/decode" \
  -F "file=@qrcode.png"
```

### Python 调用

```python
import requests, base64

BASE_URL = "https://relax-api.onrender.com/api/v1/tools/qrcode"

# 生成
resp = requests.get(f"{BASE_URL}/generate", params={"text": "https://example.com", "size": 400})
result = resp.json()
img_data = base64.b64decode(result["data"]["image"])
with open("qrcode.png", "wb") as f:
    f.write(img_data)

# 解析
with open("qrcode.png", "rb") as f:
    resp = requests.post(f"{BASE_URL}/decode", files={"file": f})
result = resp.json()
print(result["data"]["results"])
```

### JavaScript 调用

```javascript
// 生成
const text = encodeURIComponent("https://example.com");
fetch(`https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=${text}&size=300`)
  .then(res => res.json())
  .then(data => {
    const img = document.createElement("img");
    img.src = `data:${data.data.mime_type};base64,${data.data.image}`;
    document.body.appendChild(img);
  });

// 解析
const formData = new FormData();
formData.append("file", fileInput.files[0]);
fetch("https://relax-api.onrender.com/api/v1/tools/qrcode/decode", { method: "POST", body: formData })
  .then(res => res.json())
  .then(data => console.log(data.data.results));
```

---

## 5. 限制与注意事项

- 解析接口最大文件大小：**10MB**
- 生成接口二维码尺寸范围：**100–1000 像素**
- 解析需要 `pyzbar` 库及系统 `libzbar`；功能不可用时检查 `data.error` 字段
- 单张图片中的多个二维码均会返回在 `data.results` 中
- URL 含特殊字符时需在查询参数中进行 URL 编码
- 生成的二维码使用中等容错级别（M）
