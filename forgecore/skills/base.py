# forgecore/skills/base.py
"""Skill 基类 - 所有技能必须继承此类"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseSkill:
    """所有 Skill 的统一基类。子类只需实现 execute(**kwargs) -> dict"""

    def __init__(self, skill_dir: Optional[Path] = None):
        self._skill_dir = skill_dir or Path(__file__).parent
        self._meta = self._load_meta()

    def _load_meta(self) -> Dict[str, Any]:
        """从 meta.json 加载技能元信息"""
        meta_path = self._skill_dir / "meta.json"
        if meta_path.exists():
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"name": self.__class__.__name__, "version": "0.0.0"}

    @property
    def name(self) -> str:
        return self._meta.get("name", self.__class__.__name__)

    @property
    def version(self) -> str:
        return self._meta.get("version", "0.0.0")

    @property
    def description(self) -> str:
        return self._meta.get("description", "")

    def execute(self, **kwargs) -> Dict[str, Any]:
        """统一执行入口。子类必须重写此方法。"""
        raise NotImplementedError(f"{self.__class__.__name__} 未实现 execute()")

    def safe_execute(self, **kwargs) -> Dict[str, Any]:
        """带异常捕获的安全执行（GUI 调用此方法）"""
        try:
            logger.info(f"🚀 执行技能: {self.name} | 参数: {list(kwargs.keys())}")
            result = self.execute(**kwargs)
            if "status" not in result:
                result["status"] = "success"
            return result
        except Exception as e:
            import traceback
            logger.error(f"❌ 技能 {self.name} 执行失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "skill": self.name,
                "timestamp": datetime.now().isoformat(),
            }

    def __repr__(self):
        return f"<Skill:{self.name} v{self.version}>"