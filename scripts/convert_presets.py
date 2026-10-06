"""
将 templates/sd_gui/prompts/*.json 转换为 sd_forge 预设格式。

输入:
    <input_dir>/*.json     例如: shared_assets/templates/sd_gui/prompts
    每个 JSON 长这样:
        {
          "name": "动漫风格",
          "icon": "🎭",
          "priority": 6,
          "templates": [
            {"name": "色气护士", "prompt": "...", "negative": "..."},
            ...
          ]
        }

输出:
    <output_dir>/sd_forge/<分类>/<预设名>.py
    每个 template -> 一个独立 .py 文件
    分类名  = JSON 文件名去掉扩展名 (beauty_anime.json -> beauty_anime)
    预设名  = template["name"]
    文件内容 = PRESET 字典 (layers.subject 存完整 prompt)

用法:
    python scripts/convert_presets.py <input_dir> [output_dir]

示例:
    python scripts/convert_presets.py ^
        shared_assets/templates/sd_gui/prompts ^
        shared_assets/presets_by_app
"""

import json
import sys
import re
from pathlib import Path


# ============================================================
# 工具函数
# ============================================================

# Windows 文件名非法字符
_INVALID_CHARS = r'<>:"/\|?*'


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符。"""
    name = name.strip()
    for ch in _INVALID_CHARS:
        name = name.replace(ch, "_")
    # 去掉控制字符
    name = re.sub(r"[\x00-\x1f]", "", name)
    # 去掉首尾空格和点 (Windows 不允许)
    name = name.strip(" .")
    return name or "unnamed"


def py_str(s: str) -> str:
    """把字符串转成 Python 字面量 (安全转义)。"""
    return json.dumps(s, ensure_ascii=False)


def infer_category(json_stem: str) -> str:
    """从 JSON 文件名推断分类名。beauty_anime -> beauty_anime。"""
    return sanitize_filename(json_stem)


# ============================================================
# 单个 template -> 一个 .py 文件
# ============================================================

def render_preset_py(
    template: dict,
    category: str,
    source_json: str,
    icon: str = "",
    priority: int = 0,
) -> str:
    """生成一个 PRESET 的 Python 源码字符串。"""
    name = template.get("name", "unnamed")
    prompt = template.get("prompt", "")
    negative = template.get("negative", "")

    lines = []
    lines.append('"""')
    lines.append(f"预设: {name}")
    lines.append(f"分类: {category}")
    lines.append(f"来源: {source_json}")
    lines.append('"""')
    lines.append("")
    lines.append("PRESET = {")
    lines.append(f'    "name": {py_str(name)},')
    lines.append(f'    "category": {py_str(category)},')
    lines.append(f'    "icon": {py_str(icon)},')
    lines.append(f'    "priority": {priority},')
    lines.append('    "tags": [],')
    lines.append('    "layers": {')
    lines.append('        "subject": [')
    lines.append(f'            {py_str(prompt)},')
    lines.append('        ],')
    lines.append('        "scene": [],')
    lines.append('        "style": [],')
    lines.append('        "lighting": [],')
    lines.append('        "composition": [],')
    lines.append('        "quality": [],')
    lines.append('        "negative": [')
    if negative:
        lines.append(f'            {py_str(negative)},')
    lines.append('        ],')
    lines.append('        "inscription": [],')
    lines.append('    },')
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def convert_one_json(json_path: Path, sd_forge_dir: Path) -> tuple:
    """
    转换单个 JSON 文件。
    返回 (成功数, 失败数, 分类目录)
    """
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    templates = data.get("templates", [])
    if not templates:
        print(f"  [跳过] {json_path.name}: templates 为空")
        return (0, 0, None)

    icon = data.get("icon", "")
    priority = data.get("priority", 0)
    category = infer_category(json_path.stem)

    # 输出目录: sd_forge/<category>/
    out_dir = sd_forge_dir / category
    out_dir.mkdir(parents=True, exist_ok=True)

    ok, fail = 0, 0
    for t in templates:
        tname = sanitize_filename(t.get("name", "unnamed"))
        out_file = out_dir / f"{tname}.py"

        # 同名覆盖
        if out_file.exists():
            print(f"  [覆盖] {out_file.relative_to(sd_forge_dir)}")

        try:
            src = render_preset_py(
                template=t,
                category=category,
                source_json=json_path.name,
                icon=icon,
                priority=priority,
            )
            out_file.write_text(src, encoding="utf-8")
            ok += 1
        except Exception as e:
            print(f"  [失败] {json_path.name} -> {tname}: {e}")
            fail += 1

    return (ok, fail, category)


# ============================================================
# 主流程
# ============================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    output_dir = (
        Path(sys.argv[2])
        if len(sys.argv) > 2
        else Path("shared_assets/presets_by_app")
    )

    if not input_dir.is_dir():
        print(f"[错误] 输入目录不存在: {input_dir}")
        sys.exit(1)

    sd_forge_dir = output_dir / "sd_forge"
    sd_forge_dir.mkdir(parents=True, exist_ok=True)

    json_files = sorted(input_dir.glob("*.json"))
    if not json_files:
        print(f"[警告] 输入目录没有 .json 文件: {input_dir}")
        sys.exit(0)

    print("=" * 60)
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {sd_forge_dir}")
    print(f"共 {len(json_files)} 个 JSON")
    print("=" * 60)

    total_ok, total_fail = 0, 0
    for jf in json_files:
        print(f"\n📄 {jf.name}")
        ok, fail, cat = convert_one_json(jf, sd_forge_dir)
        if cat:
            print(f"  -> 分类 [{cat}]  成功 {ok}  失败 {fail}")
        total_ok += ok
        total_fail += fail

    print("\n" + "=" * 60)
    print(f"完成: 成功 {total_ok}, 失败 {total_fail}")
    print(f"输出: {sd_forge_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()