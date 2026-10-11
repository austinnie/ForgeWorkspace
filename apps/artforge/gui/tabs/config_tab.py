# apps/artforge/gui/tabs/config_tab.py
"""配置 Tab — 展示 ForgeCore 系统状态"""

import gradio as gr

from forgecore.config.registry import ModelRegistry


def build_config_tab(app) -> None:
    """构建系统状态面板。app 是 ArtForgeApp 实例，用它的 loras 数量。"""
    with gr.Group():
        gr.Markdown("### ⚙️ 系统状态")

        try:
            from forgecore.config.registry import ModelRegistry as _MR
            sd15 = len(_MR.scan_checkpoints("sd15"))
            sdxl = len(_MR.scan_checkpoints("sdxl"))
            lora_count = len(app.loras)
            gr.Markdown(
                f"**ForgeCore**: ✅ 已加载\n"
                f"**SD1.5 模型**: {sd15} 个\n"
                f"**SDXL 模型**: {sdxl} 个\n"
                f"**LoRA**: {lora_count} 个"
            )
        except Exception:
            gr.Markdown("**ForgeCore**: ❌ 未加载")