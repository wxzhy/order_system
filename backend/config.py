"""配置文件管理模块"""

import yaml
from pathlib import Path
from typing import Any

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config.yaml"


def load_config() -> dict[str, Any]:
    """加载配置文件"""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_FILE}")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config


# 全局配置对象
_config = None


def get_config() -> dict[str, Any]:
    """获取配置对象（单例模式）"""
    global _config
    if _config is None:
        _config = load_config()
    return _config
