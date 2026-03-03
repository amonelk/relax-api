# QR Code Toolkit API 文档

## 1. 概述

`qrcode` 服务提供二维码生成和解析能力，通过 HTTP 接口提供能力。

- **Base URL**：`https://relax-api.onrender.com`
- **接口列表**：
  - `GET /api/v1/tools/qrcode/generate` - 生成二维码
  - `POST /api/v1/tools/qrcode/decode` - 解析二维码
- **请求方式**：
  - `GET` 查询参数（生成）
  - `multipart/form-data`（解析）

## 2. 接口详情

### 2.1 生成二维码

- **Method**: `GET`
- **Path**: `/api/v1/tools/qrcode/generate`
- **描述**：根据文本内容生成二维码图片
- **输出格式**：PNG、JPEG、WebP

### 2.2 解析二维码

- **Method**: `POST`
- **Path**: `/api/v1/tools/qrcode/decode`
- **描述**：从图片中提取二维码内容
- **注意**：需要 `pyzbar` 库及系统 `libzbar` 依赖

## 3. 请求参数

### 3.1 生成二维码

查询参数：

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---:|---|---|
| `text` | string | 是 | - | 要编码的内容（含特殊字符需 URL 编码） |
| `size` | int | 否 | `300` | 图片尺寸（像素），范围 100-1000 |
| `format` | string | 否 | `png` | `png` / `jpeg` / `webp` |

### 3.2 解析二维码

表单字段：

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---:|---|---|
| `file` | File | 是 | - | 包含二维码的图片 |

上传限制：**10MB**

## 4. 返回结构

### 4.1 生成二维码返回

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

字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.image` | string | Base64 编码的二维码图片 |
| `data.format` | string | 输出格式 |
| `data.mime_type` | string | 图片 MIME 类型 |
| `data.text` | string | 原始编码内容 |
| `data.size` | int | 图片尺寸（像素） |

### 4.2 解析二维码返回

成功（检测到二维码）：

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

未检测到二维码：

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

功能不可用（pyzbar 未安装）：

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

## 5. 错误处理

| 场景 | HTTP 状态码 | 业务码 | 说明 |
|---|---:|---:|---|
| 文件超过 10MB | `413` | `41300` | `Uploaded file is too large. Max size is 10MB.` |
| 缺少必填参数 | `422` | - | FastAPI 校验错误结构 |
| 处理异常 | `500` | `50000` | `Internal server error: ...` |

## 6. 示例

### 6.1 生成二维码（curl）

基本用法：
```bash
curl "https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com"
```

自定义尺寸和格式：
```bash
curl "https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com&size=500&format=webp"
```

包含特殊字符的 URL（URL 编码）：
```bash
curl "https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https%3A%2F%2Fexample.com%2Fpath%3Fid%3D123"
```

### 6.2 解析二维码（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/qrcode/decode" \
  -F "file=@qrcode.png"
```

### 6.3 Python 调用

```python
import requests
import base64

BASE_URL = "https://relax-api.onrender.com/api/v1/tools/qrcode"

# 生成二维码
resp = requests.get(
    f"{BASE_URL}/generate",
    params={
        "text": "https://example.com",
        "size": 400,
        "format": "png"
    }
)
result = resp.json()

# 保存二维码图片
img_data = base64.b64decode(result["data"]["image"])
with open("qrcode.png", "wb") as f:
    f.write(img_data)
print(f"二维码已保存: {result['data']['text']}")

# 解析二维码
with open("qrcode.png", "rb") as f:
    resp = requests.post(
        f"{BASE_URL}/decode",
        files={"file": f}
    )
result = resp.json()
if result["data"]["results"]:
    print(f"解析结果: {result['data']['results'][0]['data']}")
else:
    print(f"错误: {result['data'].get('error', '未知')}")
```

### 6.4 JavaScript 调用

```javascript
// 生成二维码
const text = encodeURIComponent("https://example.com");
const url = `https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=${text}&size=300`;

fetch(url)
  .then(res => res.json())
  .then(data => {
    const img = document.createElement('img');
    img.src = `data:${data.data.mime_type};base64,${data.data.image}`;
    document.body.appendChild(img);
  });

// 解析二维码
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('https://relax-api.onrender.com/api/v1/tools/qrcode/decode', {
  method: 'POST',
  body: formData
})
  .then(res => res.json())
  .then(data => console.log(data.data.results));
```

## 7. 限制与注意事项

- **最大文件大小**：解析接口 10MB
- **二维码尺寸**：生成接口 100-1000 像素
- **解析功能**：需要 `pyzbar` 库及系统 `libzbar` 依赖
  - 部分托管平台可能不支持（如 Render 免费版）
  - 响应中检查 `data.error` 字段确认功能可用性
- **多二维码**：解析接口可检测单张图片中的多个二维码
- **文本编码**：URL 含特殊字符时需进行 URL 编码
- **容错级别**：生成的二维码使用中等容错级别（M）
