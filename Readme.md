# relax-api

统一 API 网关工程，基于 FastAPI 封装 `services/` 下工具源码，并可直接部署到 Render。

## 目录结构

- `renderapi/`：统一 Web Server API 网关
- `services/markitdown/`：工具源码封装（直接调用）
- `tests/integration/`：统一契约测试
- `scripts/sync_sources.py`：拉取上游源码脚本（当前方案依赖）

## 本地启动

```bash
python3 -m venv .venv
source .venv/bin/activate
# 首次若 upstream 不存在，先安装 pyyaml 再拉源码
pip install pyyaml
python3 scripts/sync_sources.py
# 基于本地上游源码安装 markitdown（requirements 已使用 -e 路径）
pip install -r requirements.txt
uvicorn app.main:app --app-dir renderapi --host 0.0.0.0 --port 8000
```

## 运行测试

```bash
pytest -q
```

## API 文档

基础地址（本地）：

- `http://127.0.0.1:8000`

接口列表：

- `POST /api/v1/tools/markitdown/execute`（统一转换入口：JSON 文本 + 文件上传）
- `GET /healthz`
- `GET /readyz`

### 1) JSON 文本转换

`POST /api/v1/tools/markitdown/execute`

请求头：

- `Content-Type: application/json`

请求体：

```json
{
  "payload": {
    "text": "# hello from http",
    "suffix": ".md",
    "format_mode": "enhanced",
    "use_plugins": false,
    "docintel_endpoint": null
  }
}
```

字段说明：

- `payload.text`：要转换的文本
- `payload.suffix`：临时文件后缀（例如 `.txt`、`.md`）
- `payload.use_plugins`：是否启用插件
- `payload.docintel_endpoint`：文档智能服务地址（有值即自动启用 docintel）
- `payload.format_mode`：输出格式化级别（`raw` 原样、`enhanced` 增强排版、`strict` 更激进段落合并）

### 2) 文件上传转换（统一入口）

`POST /api/v1/tools/markitdown/execute`

请求头：

- `Content-Type: multipart/form-data`

表单字段：

- `file`（File，必填）
- `use_plugins`（Text，可选，默认 `false`）
- `docintel_endpoint`（Text，可选）
- `format_mode`（Text，可选，默认 `raw`，可选 `enhanced/strict`）
- 文件大小限制：`10MB`（超过会返回 `413`）

curl 示例：

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/tools/markitdown/execute" \
  -F "file=@/path/to/demo.pdf" \
  -F "use_plugins=false" \
  -F "format_mode=raw"
```

### Apifox 配置步骤

1. 新建接口，Method 选 `POST`，URL 填：
   - `http://127.0.0.1:8000/api/v1/tools/markitdown/execute`
2. 在 `Body` 里选择 `form-data`
3. 新增参数：
   - `file`，类型选 `File`，选择本地文件
   - `use_plugins`，类型 `Text`，填 `false`
  - 需要时再加 `docintel_endpoint`、`format_mode`
4. 点击发送，返回 `code=0` 且 `data.markdown` 有内容即成功

### 响应格式（统一）

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "tool": "markitdown",
    "source": "upload:demo.pdf",
    "markdown": "..."
  },
  "request_id": "..."
}
```

实现说明：服务端通过 `services/markitdown` 中的运行逻辑执行转换，不走 CLI 命令。