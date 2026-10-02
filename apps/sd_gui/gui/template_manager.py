# gui/template_manager.py
"""极简模板管理器 - 加载 shared_assets/templates/sd_gui 下的 JSON 模板"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

class TemplateManager:
    """加载和管理 sd_gui 的提示词模板"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.template_dir = project_root / "shared_assets" / "templates" / "sd_gui"
        
        # 缓存加载的模板
        self.persons_config = {}
        self.scenes_config = {}
        self.relationships_config = {}
        self.prompt_categories = {}  # prompts/ 下的分类
        
        self._load_all()
    
    def _load_all(self):
        """加载所有模板"""
        if not self.template_dir.exists():
            print(f"⚠️ 模板目录不存在：{self.template_dir}")
            return
        
        # 1. 加载核心配置
        self.persons_config = self._load_json("persons.json")
        self.scenes_config = self._load_json("scenes.json")
        self.relationships_config = self._load_json("relationships.json")
        
        # 2. 加载 prompts/ 下的分类模板
        prompts_dir = self.template_dir / "prompts"
        if prompts_dir.exists():
            for json_file in prompts_dir.glob("*.json"):
                category_name = json_file.stem  # 如 "beauty_anime"
                self.prompt_categories[category_name] = self._load_json(f"prompts/{json_file.name}")
        
        print(f"✅ 已加载模板：{len(self.prompt_categories)} 个分类")
    
    def _load_json(self, relative_path: str) -> Dict:
        """加载 JSON 文件"""
        filepath = self.template_dir / relative_path
        if not filepath.exists():
            return {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载 {relative_path} 失败：{e}")
            return {}
    
    def get_category_names(self) -> List[str]:
        """获取所有分类名称（用于 UI 下拉框）"""
        return sorted(self.prompt_categories.keys())
    
    def get_items_in_category(self, category: str) -> List[Dict]:
        """获取分类下的所有项目"""
        data = self.prompt_categories.get(category, {})
        # 兼容两种格式：列表 或 字典
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # 如果是字典，尝试提取 items 或直接返回 values
            if "items" in data:
                return data["items"]
            return [{"name": k, "prompt": v.get("prompt", ""), "negative": v.get("negative", "")} 
                    for k, v in data.items()]
        return []
    
    def build_prompt_from_selection(self, category: str, item_name: str) -> tuple:
        """根据选择构建提示词
        返回：(prompt, negative)
        """
        items = self.get_items_in_category(category)
        for item in items:
            if item.get("name") == item_name or item.get("id") == item_name:
                return item.get("prompt", ""), item.get("negative", "")
        return "", ""
    
    def build_person_prompt(self, selections: Dict[str, str]) -> str:
        """根据人物配置构建提示词
        selections: {"age": "adult", "gender": "female", "ethnicity": "chinese", ...}
        """
        parts = []
        for category, key in selections.items():
            if category in self.persons_config and key in self.persons_config[category]:
                prompt = self.persons_config[category][key].get("prompt", "")
                if prompt:
                    parts.append(prompt)
        return ", ".join(parts)
    
    def build_scene_prompt(self, scene: str, lighting: str = "natural", quality: str = "photorealistic") -> str:
        """根据场景配置构建提示词"""
        parts = []
        # 画质
        if quality in self.scenes_config.get("画质", {}):
            parts.append(self.scenes_config["画质"][quality].get("prompt", ""))
        # 场景
        if scene in self.scenes_config.get("具体场景", {}):
            parts.append(self.scenes_config["具体场景"][scene].get("prompt", ""))
        # 灯光
        if lighting in self.scenes_config.get("灯光", {}):
            parts.append(self.scenes_config["灯光"][lighting].get("prompt", ""))
        return ", ".join(parts)