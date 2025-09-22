from __future__ import annotations
from typing import Dict, Any, Optional
import os
import yaml


def load_patterns(yaml_path: str) -> Dict[str, Any]:
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(yaml_path)
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def get_rle_by_name(data: Dict[str, Any], name: str) -> Optional[str]:
    """在 YAML 的各分类中按 name 查找 RLE。"""
    for category, items in data.get("categories", {}).items():
        for it in items:
            if it.get("name").lower() == name.lower():
                return it.get("rle")
    return None