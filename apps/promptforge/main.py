# apps/promptforge/main.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PromptForge - 全链路AI内容创作 (Monorepo 版)"""
import sys
from pathlib import Path

CORE_PATH = Path(__file__).resolve().parent.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

print("📝 PromptForge 启动，正在加载 ForgeCore...")

try:
    # 这里可以导入 forgecore 的 LLM 路由或 Export 模块
    # from forgecore.llm.router import SkillRouter
    # from forgecore.export.markdown import MarkdownExporter
    
    print("✅ PromptForge 核心模块加载就绪！")
    print("💡 提示：现在您可以将旧版的 skill 路由逻辑迁移到 apps/promptforge/skills/ 中，并调用 forgecore 的导出功能。")

except Exception as e:
    print(f"❌ 运行失败: {e}")