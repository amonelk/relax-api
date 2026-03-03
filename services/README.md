# 多工具源码集成说明

`services/` 用于承载每个工具的源码：

- `markitdown/`：工具目录
- `src/`：当前项目内的 Python 重写逻辑
- `upstream/`：保存从 GitHub 拉取的原始源码（用于二次封装）
- `CAPABILITIES.md`：能力清单与接口描述

GitHub 源仓库清单在 `services/sources.yaml` 中维护。
