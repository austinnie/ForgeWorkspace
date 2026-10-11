# forgecore/skills/meta_utils.py
"""
skill meta.json 的通用解析与格式化工具

被 GUI 用来展示 skill 说明、生成默认参数。
不依赖任何 app，任何 app 都能用。
"""

import json
from pathlib import Path
from typing import Dict, List


def load_meta(skills_dir: Path, skill_name: str) -> dict:
    """
    读某个 skill 的 meta.json。
    skills_dir 是 skills 根目录（例如 forgecore/skills）。
    读不到返回空 dict。
    """
    meta_path = Path(skills_dir) / skill_name / "meta.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def build_default_params(meta: dict) -> dict:
    """从 meta.inputs 生成默认参数字典。"""
    params: Dict[str, object] = {}
    for inp in meta.get("inputs", []):
        name = inp.get("name")
        if not name:
            continue
        if "default" in inp:
            params[name] = inp["default"]
            continue
        t = inp.get("type", "string")
        if t in ("integer", "number"):
            params[name] = 0
        elif t == "boolean":
            params[name] = False
        else:
            params[name] = ""
    return params


def format_info_md(skill_name: str, meta: dict, skill_meta: dict) -> str:
    """生成 skill 参数说明 markdown。"""
    lines: List[str] = [f"### {meta.get('name', skill_name)}"]

    desc = meta.get("description") or skill_meta.get("description") or "(无描述)"
    lines.append(f"\n{desc}\n")

    tags = skill_meta.get("tags", [])
    if tags:
        lines.append(f"**标签**: `{'` `'.join(tags)}`\n")

    version = meta.get("version") or skill_meta.get("version", "")
    if version:
        lines.append(f"**版本**: {version}\n")

    inputs = meta.get("inputs", [])
    if inputs:
        lines.append("**参数说明**:\n")
        for inp in inputs:
            req = "🟥 必填" if inp.get("required") else "⬜ 可选"
            name = inp.get("name", "?")
            typ = inp.get("type", "string")
            desc_i = inp.get("description", "")
            default = inp.get("default", "—")
            enum = inp.get("enum")
            line = f"- `{name}` ({typ}) {req} — {desc_i}"
            if enum:
                line += f" | 可选值: {enum}"
            line += f" | 默认: `{default}`"
            lines.append(line)
    else:
        lines.append("*(此 skill 无 meta.inputs，请自行构造参数 JSON)*")

    outputs = meta.get("outputs", [])
    if outputs:
        lines.append("\n**输出**:\n")
        for out in outputs:
            lines.append(f"- `{out.get('name', '?')}` — {out.get('description', '')}")

    return "\n".join(lines)