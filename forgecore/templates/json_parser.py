# forgecore/templates/json_parser.py
"""
多模式 JSON 提示词解析器

支持解析以下结构的提示词 JSON:
  A. 列表式:        [{"name": "x", "prompt": "..."}, ...]
  B. 对象式:        {"cat": {"prompt": "...", "negative": "..."}, ...}
  C. 键值对:        {"cat": "a cute cat", "dog": "a dog"}
  D. WebUI式:       {"text": "...", "negative_text": "..."}
  E. 嵌套式:        {"category": {"item": {"prompt": "..."}}}
  F. 模板数组式:    {"name": "x", "icon": "🎭", "templates": [{"name": "y", "prompt": "..."}, ...]}

统一输出: [{"name": str, "prompt": str, "negative": str}, ...]
"""

from typing import Any, Dict, List


PromptItem = Dict[str, str]

# 顶层 dict 里哪个键是"模板数组"
_TEMPLATE_ARRAY_KEYS = ("templates", "items", "prompts", "list")


def _parse_list(data: List[Any]) -> List[PromptItem]:
    """解析一个 list，每项可能是 dict / str。"""
    items: List[PromptItem] = []
    for item in data:
        if isinstance(item, dict):
            name = (
                item.get("name")
                or item.get("title")
                or item.get("id")
                or f"Item_{len(items) + 1}"
            )
            prompt = (
                item.get("prompt")
                or item.get("positive")
                or item.get("text")
                or ""
            )
            negative = (
                item.get("negative")
                or item.get("negative_prompt")
                or item.get("negative_text")
                or ""
            )
            items.append({
                "name": str(name),
                "prompt": str(prompt),
                "negative": str(negative),
            })
        elif isinstance(item, str):
            items.append({
                "name": f"Item_{len(items) + 1}",
                "prompt": item,
                "negative": "",
            })
    return items


def normalize_items(data: Any, parent_key: str = "") -> List[PromptItem]:
    """
    将各种格式的 JSON 统一转换为:
        [{"name": "...", "prompt": "...", "negative": "..."}]
    """
    items: List[PromptItem] = []

    # ---- A. 顶层是 list ----
    if isinstance(data, list):
        return _parse_list(data)

    if isinstance(data, dict):
        # ---- F. 顶层 dict 里有 templates/items/... 数组 ----
        for key in _TEMPLATE_ARRAY_KEYS:
            if key in data and isinstance(data[key], list):
                sub = _parse_list(data[key])
                if sub:
                    return sub

        # ---- B/C/D/E. 遍历 dict ----
        for k, v in data.items():
            if isinstance(v, dict):
                # B/D. dict 里直接是 prompt 对象
                if any(key in v for key in ["prompt", "positive", "text", "negative"]):
                    name = v.get("name") or v.get("title") or k
                    prompt = (
                        v.get("prompt")
                        or v.get("positive")
                        or v.get("text")
                        or ""
                    )
                    negative = v.get("negative") or v.get("negative_prompt") or ""
                    items.append({
                        "name": str(name),
                        "prompt": str(prompt),
                        "negative": str(negative),
                    })
                else:
                    # E. 嵌套分类，递归 + 父键前缀
                    sub_items = normalize_items(v, parent_key=k)
                    for sub in sub_items:
                        sub["name"] = f"{k} - {sub['name']}"
                    items.extend(sub_items)

            elif isinstance(v, str):
                # C. 纯键值对
                items.append({
                    "name": str(k),
                    "prompt": str(v),
                    "negative": "",
                })

    return items


def load_json_file(filepath) -> List[PromptItem]:
    """从 .json 文件加载并解析为统一格式。"""
    import json
    from pathlib import Path

    path = Path(filepath)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return normalize_items(data)