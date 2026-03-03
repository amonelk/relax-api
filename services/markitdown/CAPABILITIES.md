# markitdown 能力清单

- 来源仓库：`https://github.com/microsoft/markitdown.git`
- 统一接口：`execute_markitdown(payload: dict) -> dict`
- 当前已实现能力：
  - 拉取上游源码后，直接调用 `MarkItDown` Python API
  - 支持 HTTP 统一入口 `/execute`（JSON 文本 + multipart 文件上传）
  - 支持 `payload.text` 内联文本转换（服务端临时文件中转）
  - 支持 `format_mode` 二次格式化（`raw/enhanced/strict`）
  - 参数映射：`use_plugins -> MarkItDown(enable_plugins=...)`
  - 参数映射：`docintel_endpoint(非空) -> MarkItDown(docintel_endpoint=...)`
