# markitdown API 文档

## 1. 概述

`markitdown` 服务用于将文本或上传文件转换为 Markdown，通过 HTTP 接口提供能力。

- **Base URL**：`https://relax-api.onrender.com`
- **接口路径**：`POST /api/v1/tools/markitdown/execute`
- 支持两种请求方式：
  - `application/json`（文本转换）
  - `multipart/form-data`（文件上传转换）

## 2. 接口列表

### 2.1 执行转换

- **Method**: `POST`
- **Path**: `/api/v1/tools/markitdown/execute`
- **能力**:
  - 文本输入（`payload.text` 或 form `text`）
  - 文件输入（form `file`）
  - Markdown 格式后处理（`raw/enhanced/strict`）
  - 可选启用插件（`use_plugins`）
  - 可选启用 docintel（`docintel_endpoint` 非空时自动启用）

## 3. 请求参数

### 3.1 JSON 模式（`Content-Type: application/json`）

请求体结构：

```json
{
  "payload": {
    "text": "string | null",
    "suffix": ".txt",
    "format_mode": "raw | enhanced | strict",
    "use_plugins": false,
    "docintel_endpoint": "string | null"
  }
}
```

字段说明：

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---:|---|---|
| `payload` | object | 是 | - | 参数容器 |
| `payload.text` | string \| null | 否 | `null` | 文本内容，不传时按空字符串处理 |
| `payload.suffix` | string | 否 | `.txt` | 临时文件后缀 |
| `payload.format_mode` | string | 否 | `raw` | 枚举：`raw` / `enhanced` / `strict` |
| `payload.use_plugins` | bool | 否 | `false` | 是否启用插件 |
| `payload.docintel_endpoint` | string \| null | 否 | `null` | 非空时自动启用 docintel |

### 3.2 Multipart 模式（`Content-Type: multipart/form-data`）

表单字段说明：

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---:|---|---|
| `file` | File | 否 | - | 有文件则走文件转换 |
| `text` | Text | 否 | `null` | 无文件时可传文本 |
| `suffix` | Text | 否 | `.txt` | 文本模式临时后缀 |
| `format_mode` | Text | 否 | `raw` | 枚举：`raw` / `enhanced` / `strict` |
| `use_plugins` | Text(bool) | 否 | `false` | `true` / `false` |
| `docintel_endpoint` | Text | 否 | `null` | 非空时自动启用 docintel |

上传限制：

- `file` 大小上限：`10MB`
- 超限返回：HTTP `413`，业务码 `41300`

## 4. 返回结构

成功返回（统一格式）：

```json
{
  "code": 0,
  "message": "markitdown executed",
  "data": {
    "tool": "markitdown",
    "source": "inline-text",
    "format_mode": "enhanced",
    "markdown": "..."
  },
  "request_id": "uuid"
}
```

字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | int | `0` 表示成功 |
| `message` | string | 状态信息 |
| `data.tool` | string | 固定 `markitdown` |
| `data.source` | string | `inline-text` 或 `upload:<filename>` |
| `data.format_mode` | string | 实际格式模式 |
| `data.markdown` | string | 转换后的 Markdown |
| `request_id` | string | 请求追踪 ID |

## 5. 错误处理

已知错误行为：

| 场景 | HTTP 状态码 | 业务码 | 说明 |
|---|---:|---:|---|
| 上传文件超过 10MB | `413` | `41300` | `Uploaded file is too large. Max size is 10MB.` |
| 参数校验失败（如非法 `format_mode`） | `422` | - | FastAPI 校验错误结构 |
| 未捕获异常 | `500` | `50000` | `Internal server error: ...` |

统一错误结构（`AppError` / 全局异常处理）：

```json
{
  "code": 41300,
  "message": "Uploaded file is too large. Max size is 10MB.",
  "data": {},
  "request_id": "uuid"
}
```

## 6. 示例

### 6.1 JSON 文本转换（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "text": "# hello from http",
      "suffix": ".md",
      "format_mode": "enhanced",
      "use_plugins": false,
      "docintel_endpoint": null
    }
  }'
```

### 6.2 文件上传转换（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -F "file=@/path/to/demo.pdf" \
  -F "format_mode=strict" \
  -F "use_plugins=false"
```

### 6.3 Python 调用

```python
import requests

url = "https://relax-api.onrender.com/api/v1/tools/markitdown/execute"
resp = requests.post(
    url,
    json={
        "payload": {
            "text": "# Title",
            "format_mode": "enhanced",
            "use_plugins": False,
            "docintel_endpoint": None,
        }
    },
    timeout=60,
)
print(resp.status_code, resp.json())
```

## 7. 限制与注意事项

- 当前服务文档基于现有代码行为，未覆盖所有潜在输入类型与边界场景。
- `format_mode` 仅支持：`raw` / `enhanced` / `strict`。
- `docintel_endpoint` 为空时不会启用 docintel。
- 接口为 HTTP 场景设计，不提供本地结果写入路径参数。
