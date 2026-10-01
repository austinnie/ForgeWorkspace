# forgecore/prompt/__init__.py
"""提示词工坊 - 统一导出"""

# 尝试导入 ArtForge 的 PromptBuilder
try:
    from .builder import PromptBuilder
except ImportError:
    PromptBuilder = None

# 尝试导入 LayerForge 的 PromptComposer
try:
    from .composer import PromptComposer
except ImportError:
    PromptComposer = None

__all__ = ["PromptBuilder", "PromptComposer"]
