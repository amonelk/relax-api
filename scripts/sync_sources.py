from __future__ import annotations

import subprocess
from pathlib import Path

import yaml


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def sync_tool(repo_url: str, branch: str, local_path: Path) -> None:
    if local_path.exists() and any(local_path.iterdir()):
        print(f"[skip] {local_path} already exists and is not empty")
        return
    local_path.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", "--depth", "1", "--branch", branch, repo_url, str(local_path)])
    print(f"[ok] cloned {repo_url} -> {local_path}")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    source_file = repo_root / "services" / "sources.yaml"
    config = yaml.safe_load(source_file.read_text(encoding="utf-8"))
    tools = config.get("tools", [])

    for tool in tools:
        sync_tool(
            repo_url=tool["repo_url"],
            branch=tool.get("branch", "main"),
            local_path=repo_root / tool["local_path"],
        )


if __name__ == "__main__":
    main()
