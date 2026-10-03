# apps/artforge/gui/unified_app.py
"""
ArtForge Ultimate - 超级工作台 (完整版)
1. 完整复用 app.py 的 ArtForgeApp 类 (预设/模型/LoRA/后处理)
2. 完整的 ControlNet 流程 (含参考图上传、模型路径获取)
3. 90 个技能的全局调度
"""
import gradio as gr
import sys
import os
import json
import logging
from pathlib import Path
from PIL import Image

# ==========================================
# 1. 路径注入 & 环境初始化
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH, override=True)
    except ImportError:
        pass

# ==========================================
# 2. 导入核心模块
# ==========================================
try:
    from forgecore.skills.manager import SkillManager, skill_manager
    from forgecore.config.registry import ModelRegistry
    from forgecore.engines import create_engine
    print("✅ ForgeCore 基盘加载成功")
except ImportError as e:
    print(f"❌ ForgeCore 加载失败: {e}")
    sys.exit(1)

# 导入 app.py 的 ArtForgeApp 类 (复用其预设扫描/生图/后处理逻辑)
try:
    from apps.artforge.gui.app import ArtForgeApp
    print("✅ ArtForgeApp (app.py) 导入成功")
except ImportError as e:
    print(f"❌ app.py 导入失败: {e}")
    ArtForgeApp = None

# 初始化技能管理器
skill_manager.scan()

# ==========================================
# 3. Tab 1: 东方艺术 (100% 复用 app.py 逻辑)
# ==========================================
def build_art_forge_tab(app_instance: ArtForgeApp):
    """构建东方艺术 Tab (直接调用 app.py 的 _build_generation_tab)"""
    with gr.Tab("🎨 东方艺术"):
        # 直接复用 app.py 的 UI 构建方法，所有组件和事件绑定都会在这里生成
        app_instance._build_generation_tab()


# ==========================================
# 4. Tab 2: 通用生图 & ControlNet (完整参数)
# ==========================================
def build_controlnet_tab(app_instance: ArtForgeApp):
    with gr.Tab(" 通用生图 & ControlNet"):
        gr.Markdown("### 🧍 通用生图 (调用 forgecore.controlnet skill)")
        gr.Markdown("💡 **注意**：ControlNet 必须上传参考图，并选择本地模型")
        
        with gr.Row():
            with gr.Column(scale=1):
                # 模型选择 (复用 app 的模型扫描)
                cn_model_dd = gr.Dropdown(
                    choices=app_instance._get_models("sd15"),
                    label="选择本地模型 (SD1.5)",
                    value=app_instance._get_models("sd15")[0] if app_instance._get_models("sd15") else None
                )
                
                # 提示词
                cn_prompt = gr.Textbox(label="提示词 (Prompt)", value="1girl, standing, masterpiece", lines=2)
                cn_neg = gr.Textbox(label="负面提示词", value="worst quality, lowres", lines=1)
                
                # ControlNet 参数
                cn_type_dd = gr.Dropdown(
                    choices=["openpose", "canny", "depth", "lineart", "hed"],
                    label="ControlNet 类型",
                    value="openpose"
                )
                cn_strength = gr.Slider(0.1, 1.0, value=0.6, label="ControlNet 强度")
                
                # 参考图上传 (关键！)
                cn_img_input = gr.Image(label="📎 上传参考图 (Control Source)", type="pil")
                
                cn_btn = gr.Button("🚀 生成 (ControlNet)", variant="primary", size="lg")
                
            with gr.Column(scale=1):
                cn_out = gr.Image(label="生成结果", type="pil")
                cn_log = gr.Textbox(label="生成日志", lines=10)

        def run_controlnet(model_name, prompt, negative, cn_type, strength, ref_image):
            logs = [" 启动 ControlNet 流水线..."]
            
            if not ref_image:
                return None, "❌ 请上传参考图！ControlNet 需要参考图来提取姿态/边缘。"
            if not model_name:
                return None, "❌ 请选择本地模型。"

            try:
                # 1. 获取模型绝对路径 (复用 app.py 的逻辑)
                model_path = None
                found_in_type = "sd15"
                for m_type in ["sd15", "sdxl"]:
                    models = ModelRegistry.scan_checkpoints(m_type)
                    for m in models:
                        if m["name"] == model_name:
                            model_path = m["absolute_path"]
                            found_in_type = m_type
                            break
                    if model_path: break
                
                if not model_path:
                    return None, f"❌ 找不到模型: {model_name}"
                logs.append(f"📂 模型路径: {model_path} (类型: {found_in_type})")

                # 2. 调用 ControlNet Skill
                logs.append(f"🎛️ 调用 ControlNet Skill (类型: {cn_type})...")
                
                result = skill_manager.run(
                    "controlnet",
                    action="generate",
                    image=ref_image,
                    prompt=prompt,
                    negative_prompt=negative,
                    controlnet_type=cn_type,
                    model_path=model_path,
                    controlnet_conditioning_scale=strength,
                    num_inference_steps=20,
                    guidance_scale=7.5
                )

                if result.get("status") == "success":
                    out_path = result["result"].get("output_path")
                    if out_path and Path(out_path).exists():
                        logs.append(f"✅ 生成成功: {Path(out_path).name}")
                        return Image.open(out_path), "\n".join(logs)
                    else:
                        logs.append("⚠️ 生成成功但未找到输出图片路径")
                        return None, "\n".join(logs)
                else:
                    logs.append(f"❌ 失败: {result.get('error')}")
                    return None, "\n".join(logs)

            except Exception as e:
                return None, f"❌ 执行出错: {str(e)}"

        cn_btn.click(
            fn=run_controlnet,
            inputs=[cn_model_dd, cn_prompt, cn_neg, cn_type_dd, cn_strength, cn_img_input],
            outputs=[cn_out, cn_log]
        )


# ==========================================
# 5. Tab 3: 技能中心 (90 Skills 动态调度)
# ==========================================
def build_skill_hub_tab():
    with gr.Tab("🛠️ 技能中心 (90 Skills)"):
        gr.Markdown("### 🚀 ForgeCore 全局技能调度器")
        gr.Markdown("💡 **提示**：参数需填写合法的 JSON 格式。")
        
        skill_names = [s['name'] for s in skill_manager.list_skills()]
        
        with gr.Row():
            with gr.Column(scale=1):
                skill_dd = gr.Dropdown(
                    choices=skill_names, 
                    label="选择技能", 
                    value="search_engine" if "search_engine" in skill_names else skill_names[0]
                )
                params_input = gr.Textbox(
                    label="执行参数 (JSON 格式)",
                    value='{"query": "AI 绘画", "kind": "images", "limit": 5}',
                    lines=6
                )
                run_btn = gr.Button("🚀 执行技能", variant="primary", size="lg")
            with gr.Column(scale=1):
                log_output = gr.Textbox(label="执行日志", lines=12, interactive=False)
                result_output = gr.JSON(label="返回结果")

        def execute_skill(skill_name, params_json):
            logs = [f" 执行: {skill_name}"]
            try:
                kwargs = json.loads(params_json) if params_json.strip() else {}
                result = skill_manager.run(skill_name, **kwargs)
                if result.get("status") == "success":
                    logs.append("✅ 成功")
                    for k, v in result.get("result", {}).items():
                        if isinstance(v, str) and "path" in k.lower():
                            logs.append(f" 📂 {k}: {v}")
                else:
                    logs.append(f"❌ 失败: {result.get('error')}")
                return "\n".join(logs), result
            except Exception as e:
                return f"❌ 错误: {e}", {}

        run_btn.click(fn=execute_skill, inputs=[skill_dd, params_input], outputs=[log_output, result_output])


# ==========================================
# 6. 构建主 GUI
# ==========================================
def build_unified_gui():
    if not ArtForgeApp:
        return gr.Blocks().update() # 防止崩溃
    
    # 实例化 ArtForgeApp (加载预设、LoRA 等)
    app = ArtForgeApp()
    
    with gr.Blocks(
        title="ArtForge Ultimate · 全能 AI 创作工作台", 
        theme=gr.themes.Soft()
    ) as demo:
        
        with gr.Row():
            gr.Markdown("# 🎎 ArtForge Ultimate")
            gr.Markdown(f"**状态**: 🟢 ForgeCore 就绪 | **技能**: {len(skill_manager.list_skills())} 个")
            
        with gr.Tabs():
            # Tab 1: 东方艺术 (100% 复用 app.py)
            build_art_forge_tab(app)
            
            # Tab 2: ControlNet (完整参数：参考图+模型)
            build_controlnet_tab(app)
            
            # Tab 3: 技能中心
            build_skill_hub_tab()

    return demo

if __name__ == "__main__":
    demo = build_unified_gui()
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, inbrowser=True)