# markitdown API 文档

## 1. 概述

`markitdown` 服务用于将文本或上传文件转换为 Markdown，通过单一 HTTP 接口提供能力。

- **Base URL**：`https://relax-api.onrender.com`
- **接口路径**：`POST /api/v1/tools/markitdown/execute`
- **支持请求方式**：
  - `application/json` — 文本转换
  - `multipart/form-data` — 文件上传转换

---

## 2. 接口详情

### `POST /api/v1/tools/markitdown/execute` — 执行转换

**描述**：将文本或上传文件转换为 Markdown。`file` 与 `text` 至少提供一个。文件大小上限：10MB。

**能力**：
- 文本输入（`text` 字段）
- 文件上传（`file` 字段）：支持 PDF、Word、PPT、Excel 等格式
- Markdown 格式后处理（`raw` / `enhanced` / `strict`）
- 可选启用插件（`use_plugins`）
- 可选启用 Document Intelligence（`docintel_endpoint`）

---

#### 方式一 — JSON（`Content-Type: application/json`）

**请求参数**

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---|---|---|
| `payload.text` | string \| null | 否 | `null` | 要转换的文本内容 |
| `payload.suffix` | string | 否 | `.txt` | 文本模式下的临时文件后缀 |
| `payload.format_mode` | string | 否 | `raw` | `raw` / `enhanced` / `strict` |
| `payload.use_plugins` | bool | 否 | `false` | 是否启用插件 |
| `payload.docintel_endpoint` | string \| null | 否 | `null` | 非空时自动启用 docintel |

**请求体：**

```json
{
  "payload": {
    "text": "# Hello World",
    "suffix": ".md",
    "format_mode": "enhanced",
    "use_plugins": false,
    "docintel_endpoint": null
  }
}
```

---

#### 方式二 — 文件上传（`Content-Type: multipart/form-data`）

**请求参数**

| 字段 | 类型 | 必填 | 默认值 | 约束 |
|---|---|---|---|---|
| `file` | File | 否 | — | 有文件则走文件转换，最大 10MB |
| `text` | string | 否 | `null` | 无文件时传入文本内容 |
| `suffix` | string | 否 | `.txt` | 文本模式临时后缀 |
| `format_mode` | string | 否 | `raw` | `raw` / `enhanced` / `strict` |
| `use_plugins` | bool | 否 | `false` | `true` / `false` |
| `docintel_endpoint` | string | 否 | — | 非空时自动启用 docintel |

**请求体（文件上传）：**

```json
{
  "file": "<binary: document.pdf>",
  "format_mode": "enhanced",
  "use_plugins": false
}
```

**请求体（纯文本）：**

```json
{
  "text": "Hello World",
  "suffix": ".txt",
  "format_mode": "raw"
}
```

---

#### 返回

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
  "request_id": "uuid"
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.tool` | string | 固定为 `markitdown` |
| `data.source` | string | `inline-text` 或 `upload:<filename>` |
| `data.format_mode` | string | 实际生效的格式模式 |
| `data.markdown` | string | 转换后的 Markdown 内容 |

---

## 3. 错误处理

| 场景 | HTTP 状态码 | 业务码 | 说明 |
|---|---|---|---|
| 文件超过 10MB | `413` | `41300` | `Uploaded file is too large. Max size is 10MB.` |
| 非法 `format_mode` | `422` | — | FastAPI 校验错误 |
| 未捕获异常 | `500` | `50000` | `Internal server error: ...` |

错误返回结构：

```json
{
  "code": 41300,
  "message": "Uploaded file is too large. Max size is 10MB.",
  "data": {},
  "request_id": "uuid"
}
```

---

## 4. 示例

### JSON 文本转换（curl）

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

### 文件上传转换（curl）

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -F "file=@document.pdf" \
  -F "format_mode=strict" \
  -F "use_plugins=false"
```

### Python 调用

```python
import requests

url = "https://relax-api.onrender.com/api/v1/tools/markitdown/execute"

# JSON 模式
resp = requests.post(url, json={
    "payload": {
        "text": "# 标题",
        "format_mode": "enhanced",
        "use_plugins": False,
        "docintel_endpoint": None,
    }
}, timeout=60)
print(resp.json()["data"]["markdown"])

# 文件上传模式
with open("document.pdf", "rb") as f:
    resp = requests.post(url, files={"file": f}, data={"format_mode": "raw"}, timeout=60)
print(resp.json()["data"]["markdown"])
```

---

## 5. 限制与注意事项

- `format_mode` 仅支持：`raw` / `enhanced` / `strict`
- `docintel_endpoint` 非空时才启用 docintel
- `file` 与 `text` 至少提供一个；同时提供时，`file` 优先
