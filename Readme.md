# relax-api

从 GitHub 拉取工具源码并封装为 HTTP API，部署在 [Render](https://render.com)。

**线上地址**：`https://relax-api.onrender.com`

## 目录结构

推送地址：https://github.com/amonelk/relax-api

```
relax-api/
├── renderapi/          # FastAPI 应用（Web Server）
│   └── app/
│       ├── api/        # 路由与接口定义
│       ├── core/       # 错误处理、响应封装
│       ├── schemas/    # 请求/响应数据结构
│       └── loaders/    # 工具模块动态加载
├── services/           # 各工具的源码封装
│   ├── markitdown/     # markitdown 工具
│   ├── image/          # 图片处理工具
│   └── qrcode/         # 二维码工具
├── docs/               # API 接口文档（中英文）
├── scripts/            # 工具脚本（拉取上游源码等）
├── tests/              # 集成测试
├── requirements.txt
└── render.yaml         # Render 部署配置
```

## 已有服务

| 服务 | 接口 | 说明 | 文档 |
|---|---|---|---|
| markitdown | `POST /api/v1/tools/markitdown/execute` | 文本 / 文件转 Markdown | [中文](docs/markitdown.zh.md) · [EN](docs/markitdown.en.md) |
| image | `POST /api/v1/tools/image/{action}` | 图片处理（压缩/缩放/转换/水印） | [中文](docs/image.zh.md) · [EN](docs/image.en.md) |
| qrcode | `GET/POST /api/v1/tools/qrcode/{action}` | 二维码生成 / 解析 | [中文](docs/qrcode.zh.md) · [EN](docs/qrcode.en.md) |

### markitdown

文档转 Markdown，支持 PDF、Word、PPT、Excel 等格式。

```bash
curl -X POST "https://relax-api.onrender.com/api/v1/tools/markitdown/execute" \
  -F "file=@document.pdf"
```

### image

图片处理工具集：

| 接口 | 功能 |
|---|---|
| `POST /compress` | 压缩图片（可调质量） |
| `POST /resize` | 调整尺寸（支持多种缩放模式） |
| `POST /convert` | 格式转换（webp/jpeg/png/avif） |
| `POST /watermark` | 添加文字水印 |

```bash
# 压缩图片
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/compress" \
  -F "file=@photo.jpg" \
  -F "quality=70"

# 转换为 WebP
curl -X POST "https://relax-api.onrender.com/api/v1/tools/image/convert" \
  -F "file=@photo.png" \
  -F "format=webp"
```

### qrcode

二维码生成与解析：

| 接口 | 功能 |
|---|---|
| `GET /generate` | 生成二维码 |
| `POST /decode` | 解析二维码 |

```bash
# 生成二维码
curl "https://relax-api.onrender.com/api/v1/tools/qrcode/generate?text=https://example.com&size=300"

# 解析二维码
curl -X POST "https://relax-api.onrender.com/api/v1/tools/qrcode/decode" \
  -F "file=@qrcode.png"
```

---

健康检查：`GET /healthz` · `GET /readyz`

## 本地开发

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pyyaml
python3 scripts/sync_sources.py
pip install -r requirements.txt
uvicorn app.main:app --app-dir renderapi --host 0.0.0.0 --port 8000
```

运行测试：

```bash
pytest -q
```

## 新增工具

1. **创建工具目录**：在 `services/<tool>/src/<tool>_tool/` 下实现核心逻辑
   - `__init__.py`：实现 `execute_<tool>(action, payload) -> dict`
   - `core.py`：导出入口

2. **添加路由**：在 `renderapi/app/api/routes/` 添加 `<tool>.py`

3. **注册路由**：在 `renderapi/app/api/router.py` 中引入并注册

4. **配置加载器**：在 `renderapi/app/loaders/tool_loader.py` 添加路径映射

5. **更新依赖**：在 `requirements.txt` 添加所需依赖

6. **编写文档**：在 `docs/` 添加 `<tool>.zh.md` 和 `<tool>.en.md`
   - 概述、接口详情、请求参数、返回结构、错误处理、示例、限制与注意事项

7. **更新 README**：在服务表格和详情部分添加新工具说明
