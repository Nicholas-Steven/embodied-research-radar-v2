"""
配置加载器：统一读取 config/*.yaml 与环境变量。
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def load_yaml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / f"{name}.yaml"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_all_config() -> dict[str, Any]:
    """加载全部配置文件，合并为一个 dict。"""
    return {
        "site": load_yaml("site"),
        "topics": load_yaml("topics"),
        "queries": load_yaml("queries"),
        "scoring": load_yaml("scoring"),
        "my_research": load_yaml("my_research"),
        "ai": load_yaml("ai"),
    }


def env(key: str, default: str | None = None) -> str | None:
    """读取环境变量，缺失返回 default。"""
    return os.environ.get(key, default)


def ai_config() -> dict[str, Any]:
    """
    解析 AI 配置：从 config/ai.yaml + 环境变量。
    返回 dict 含 provider/base_url/api_key/model/enabled。
    """
    cfg = load_yaml("ai")
    provider = env("LLM_PROVIDER", cfg.get("default_provider", "openai_compatible"))
    providers = cfg.get("providers", {})
    pcfg = providers.get(provider, {})

    base_url_env = pcfg.get("base_url_env", "LLM_BASE_URL")
    api_key_env = pcfg.get("api_key_env", "LLM_API_KEY")
    model_env = pcfg.get("model_env", "LLM_MODEL")

    return {
        "provider": provider,
        "base_url": env(base_url_env, ""),
        "api_key": env(api_key_env, ""),
        "model": env(model_env, pcfg.get("default_model", "deepseek-chat")),
        "enabled": cfg.get("enabled", True),
        "timeout_seconds": pcfg.get("timeout_seconds", 60),
        "max_retries": pcfg.get("max_retries", 3),
    }
