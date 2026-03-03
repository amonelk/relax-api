# relax-api

从 GitHub 拉取工具源码并封装为 HTTP API，部署在 [Render](https://render.com)。

**线上地址**：`https://relax-api.onrender.com`

## 目录结构

```
relax-api/
├── renderapi/          # FastAPI 应用（Web Server）
│   └── app/
│       ├── api/        # 路由与接口定义
│       ├── core/       # 错误处理、响应封装
│       ├── schemas/    # 请求/响应数据结构
│       └── loaders/    # 工具模块动态加载
├── services/           # 各工具的源码封装
│   └── markitdown/     # markitdown 工具
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

1. 在 `services/` 下添加工具目录，实现 `execute_<tool>(payload) -> dict`
2. 在 `renderapi/app/api/routes/` 添加对应路由文件
3. 在 `renderapi/app/api/router.py` 注册路由
4. 在 `services/sources.yaml` 补充上游源码配置（如需拉取）
