# forgecore/skills/manager.py
"""
全局技能调度器 - 自动发现 & 统一管理
用法:
    from forgecore.skills import SkillManager
    mgr = SkillManager()
    result = mgr.run("image_curator", directory="output/daily")
"""
import importlib
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# forgecore/skills/ 目录
SKILLS_ROOT = Path(__file__).resolve().parent


class SkillManager:
    """全局技能管理器 (单例)"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._registry: Dict[str, Dict[str, Any]] = {}
            cls._instance._cache: Dict[str, Any] = {}
            cls._instance._scanned = False
        return cls._instance

    # ──────────────────────────────────────────────
    #  自动发现
    # ──────────────────────────────────────────────
    def scan(self, force: bool = False) -> int:
        """扫描 SKILLS_ROOT 下所有含 meta.json 的子目录"""
        if self._scanned and not force:
            return len(self._registry)

        self._registry.clear()
        count = 0

        for child in sorted(SKILLS_ROOT.iterdir()):
            if not child.is_dir():
                continue
            if child.name.startswith(("_", ".")):
                continue

            meta_path = child / "meta.json"
            if not meta_path.exists():
                continue

            try:
                # 新代码
                with open(meta_path, "r", encoding="utf-8-sig") as f:
                    meta = json.load(f)

                skill_name = meta.get("name", child.name)
                self._registry[skill_name] = {
                    "dir": child,
                    "meta": meta,
                    "module_name": child.name,
                }
                count += 1
            except Exception as e:
                logger.warning(f"⚠️ 跳过 {child.name}: {e}")

        self._scanned = True
        logger.info(f"✅ 技能扫描完成: 发现 {count} 个技能")
        return count

    # ──────────────────────────────────────────────
    #  查询
    # ──────────────────────────────────────────────
    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有已注册技能的摘要"""
        self.scan()
        return [
            {
                "name": name,
                "version": info["meta"].get("version", "?"),
                "description": info["meta"].get("description", ""),
                "tags": info["meta"].get("tags", []),
            }
            for name, info in self._registry.items()
        ]

    # ──────────────────────────────────────────────
    #  加载 & 执行
    # ──────────────────────────────────────────────
    def load_skill(self, skill_name: str):
        """动态加载并缓存 Skill 实例 (兼容未继承 BaseSkill 的旧技能)"""
        self.scan()

        if skill_name in self._cache:
            return self._cache[skill_name]

        info = self._registry.get(skill_name)
        if not info:
            raise ValueError(f"❌ 未知技能: {skill_name}")

        module_name = info["module_name"]
        full_module = f"forgecore.skills.{module_name}.skill"

        try:
            mod = importlib.import_module(full_module)
        except ImportError as e:
            raise ImportError(f"❌ 无法导入 {full_module}: {e}")

        # 1. 优先找继承自 BaseSkill 的类
        from forgecore.skills.base import BaseSkill
        skill_cls = None
        
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseSkill) and attr is not BaseSkill:
                skill_cls = attr
                break

        # 2. 回退机制：找任何名为 "Skill" 或有 "execute" 方法的类 (兼容旧技能)
        if not skill_cls:
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if isinstance(attr, type) and (attr_name.endswith("Skill") or hasattr(attr, "execute")):
                    skill_cls = attr
                    break
                    
        # 3. 终极回退：如果模块本身有 execute 函数（非类）
        if not skill_cls and hasattr(mod, "execute"):
            class FuncWrapper(BaseSkill):
                def execute(self, **kwargs): return mod.execute(**kwargs)
            skill_cls = FuncWrapper

        if not skill_cls:
            raise RuntimeError(f"❌ 在 {full_module} 中找不到可用的 Skill 类或 execute 函数")

        # 实例化 (处理不同构造函数的兼容性)
        try:
            instance = skill_cls(skill_dir=info["dir"])
        except TypeError:
            instance = skill_cls() # 旧技能可能不需要 skill_dir 参数
            
        self._cache[skill_name] = instance
        logger.info(f"✅ 技能加载成功: {skill_name} -> {skill_cls.__name__}")
        return instance
        
    def run(self, skill_name: str, **kwargs) -> Dict[str, Any]:
        """统一执行入口 (GUI / CLI 都调这个)"""
        try:
            skill = self.load_skill(skill_name)
            if hasattr(skill, "safe_execute"):
                return skill.safe_execute(**kwargs)
            return skill.execute(**kwargs)
        except Exception as e:
            logger.error(f"💥 调度失败 [{skill_name}]: {e}")
            return {"status": "error", "error": str(e), "skill": skill_name}


# 全局单例
skill_manager = SkillManager()