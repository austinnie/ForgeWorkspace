# forgecore/templates/manager.py
"""
模板管理器：扫描目录，加载所有 JSON 提示词模板

用法:
    from forgecore.templates.manager import TemplateManager

    tm = TemplateManager(Path("shared_assets/templates/sd_gui"))
    print(tm.categories.keys())        # {'animal': [...], 'beauty_anime': [...]}
    items = tm.categories["animal"]    # [{"name": ..., "prompt": ..., "negative": ...}]
"""

from pathlib import Path
from typing import Dict, List

from .json_parser import load_json_file, PromptItem


class TemplateManager:
    """扫描目录下的 JSON 提示词模板，统一解析为 PromptItem 列表。"""

    def __init__(self, template_dir: Path, recursive: bool = False):
        self.template_dir = Path(template_dir)
        self.categories: Dict[str, List[PromptItem]] = {}
        self._load_all(recursive=recursive)

    def _load_all(self, recursive: bool = False):
        if not self.template_dir.exists():
            print(f"⚠️ 模板目录不存在: {self.template_dir}")
            return

        pattern = "**/*.json" if recursive else "*.json"
        for json_file in sorted(self.template_dir.glob(pattern)):
            self._load_one(json_file)

    def _load_one(self, filepath: Path):
        try:
            items = load_json_file(filepath)
            if not items:
                return
            category_name = filepath.stem
            # 重名时加后缀
            base = category_name
            counter = 1
            while category_name in self.categories:
                category_name = f"{base}_{counter}"
                counter += 1
            self.categories[category_name] = items
        except Exception as e:
            print(f"⚠️ 加载模板失败 {filepath.name}: {e}")

    def list_categories(self) -> List[str]:
        return sorted(self.categories.keys())

    def get_items(self, category: str) -> List[PromptItem]:
        return self.categories.get(category, [])