# forgecore/prompt/preset_engine.py
"""
通用预设组合引擎

职责：
  - 扫描 shared_assets/presets_by_app/<lib>/<cat>/*.py
  - 加载单个 PRESET dict（带缓存）
  - 按 7 层顺序组合正向 + 负向 prompt
  - preset 某层为空时，回退到 default_layers 对应层

7 层顺序：
  subject / scene / style / lighting / composition / inscription / quality
"""

import importlib.util
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ============================================================
# 常量
# ============================================================

LAYER_ORDER = [
    "subject",
    "scene",
    "style",
    "lighting",
    "composition",
    "inscription",
    "quality",
]

DEFAULT_NEGATIVE = (
    "worst quality, low quality, blurry, ugly, deformed, "
    "bad anatomy, bad hands, extra fingers, missing fingers, "
    "watermark, text overlay, modern logo, "
    "jpeg artifacts, oversaturated, "
    "3d render, cgi, plastic look"
)


class PresetEngine:
    """通用预设组合引擎（库 / 分类 / 预设 三级）"""

    LAYER_ORDER = LAYER_ORDER
    DEFAULT_NEGATIVE = DEFAULT_NEGATIVE

    def __init__(
        self,
        presets_base: Path,
        default_layers: Optional[Dict[str, List[str]]] = None,
        auto_load_default: bool = True,
    ):
        """
        Args:
            presets_base: preset 根目录，例如 shared_assets/presets_by_app
            default_layers: 默认 7 层，preset 某层为空时回退到这里
            auto_load_default: 当 default_layers=None 时，尝试从 apps/artforge/layers 加载
        """
        self.presets_base = Path(presets_base)

        if default_layers is not None:
            self.default_layers: Dict[str, List[str]] = {
                k: list(v) for k, v in default_layers.items() if v
            }
        elif auto_load_default:
            self.default_layers = self._try_load_artforge_layers()
        else:
            self.default_layers = {}

        self._cache: Dict[str, dict] = {}

    # ========================================================
    # 默认层
    # ========================================================

    def _try_load_artforge_layers(self) -> Dict[str, List[str]]:
        """尝试加载 apps/artforge/layers 的 7 层。失败返回空 dict。"""
        try:
            from apps.artforge.layers import load_all_layers
            layers = load_all_layers()
            return {k: list(v) for k, v in layers.items() if v}
        except Exception:
            return {}

    # ========================================================
    # 扫描（库 / 分类 / 预设）
    # ========================================================

    def list_libraries(self) -> List[str]:
        """列出 presets_base 下所有库（一级子目录）。"""
        if not self.presets_base.exists():
            return []
        return sorted([
            d.name for d in self.presets_base.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        ])

    def list_categories(self, lib: str) -> List[str]:
        """列出某库下所有分类（二级子目录）。"""
        lib_dir = self.presets_base / lib
        if not lib_dir.exists():
            return []
        return sorted([
            d.name for d in lib_dir.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        ])

    def list_presets(self, lib: str, category: str) -> List[dict]:
        """
        列出某分类下所有 preset（已加载的 dict）。
        每个 dict 会带 file_path 字段。
        """
        cat_dir = self.presets_base / lib / category
        if not cat_dir.exists():
            return []

        result = []
        for py_file in sorted(cat_dir.glob("*.py")):
            if py_file.name.startswith("_") or py_file.name == "__init__.py":
                continue
            preset = self._load_preset_file(py_file)
            if preset and "name" in preset:
                result.append(preset)
        return result

    def list_preset_names(self, lib: str, category: str) -> List[str]:
        """只返回 preset 名字列表，方便 UI 用。"""
        return [p["name"] for p in self.list_presets(lib, category)]

    # ========================================================
    # 加载单个 preset
    # ========================================================

    def load_preset(
        self, lib: str, category: str, preset_name: str
    ) -> Optional[dict]:
        """按库 / 分类 / 预设名加载。"""
        for preset in self.list_presets(lib, category):
            if preset.get("name") == preset_name:
                return preset
        return None

    def _load_preset_file(self, path: Path) -> Optional[dict]:
        """从 .py 文件加载 PRESET dict，带缓存。"""
        cache_key = str(path)
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            spec = importlib.util.spec_from_file_location(
                f"preset_{path.stem}", path
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            preset = getattr(mod, "PRESET", None)
            if not isinstance(preset, dict):
                return None
            preset["file_path"] = str(path)
            self._cache[cache_key] = preset
            return preset
        except Exception as e:
            print(f"⚠️ 加载 preset 失败 {path.name}: {e}")
            return None

    # ========================================================
    # 组合
    # ========================================================

    def build_prompt(
        self,
        preset: dict,
        use_default_layers: bool = True,
    ) -> Tuple[str, str]:
        """
        组合正向 + 负向 prompt。

        Returns:
            (positive, negative)
        """
        if not preset:
            return "", self.DEFAULT_NEGATIVE

        preset_layers = preset.get("layers", {}) or {}

        parts: List[str] = []
        for key in LAYER_ORDER:
            candidates = list(preset_layers.get(key) or [])
            if not candidates and use_default_layers:
                candidates = list(self.default_layers.get(key) or [])
            if candidates:
                chosen = random.choice(candidates)
                if chosen and chosen.strip():
                    parts.append(chosen.strip())

        positive = ", ".join(parts)

        preset_neg = preset_layers.get("negative") or []
        if preset_neg:
            negative = ", ".join(x.strip() for x in preset_neg if x and x.strip())
        else:
            negative = self.DEFAULT_NEGATIVE

        return positive, negative

    def build_prompt_by_name(
        self,
        lib: str,
        category: str,
        preset_name: str,
        use_default_layers: bool = True,
    ) -> Tuple[str, str]:
        """按 库 / 分类 / 预设名 加载并组合。"""
        preset = self.load_preset(lib, category, preset_name)
        if not preset:
            return "", self.DEFAULT_NEGATIVE
        return self.build_prompt(preset, use_default_layers=use_default_layers)

    # ========================================================
    # 工具
    # ========================================================

    def get_layer_info(self, preset: dict) -> Dict[str, int]:
        """返回某 preset 各层候选数量（含回退后的）。"""
        preset_layers = preset.get("layers", {}) or {}
        info = {}
        for key in LAYER_ORDER:
            preset_count = len(preset_layers.get(key) or [])
            default_count = len(self.default_layers.get(key) or [])
            info[key] = preset_count if preset_count else default_count
        return info