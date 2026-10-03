# apps/artforge/gui/unified_app.py
"""
ArtForge Ultimate - 超级工作台 (最终完整版 + 自动保存图片功能)
1. 完整复用 app.py 的 ArtForgeApp 类 (预设/模型/后处理)
2. 通用生图 Tab (支持 Agnes API 图生图 / 本地 ControlNet 切换)
3. 90 个技能的全局智能调度
4. 🆕 全局自动保存图片功能 (统一保存到 output 目录)
"""
import gradio as gr
import sys
import os
import json
import logging
from pathlib import Path
from PIL import Image
from datetime import datetime

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

# 导入 app.py 的 ArtForgeApp 类
try:
    from apps.artforge.gui.app import ArtForgeApp
    print("✅ ArtForgeApp (app.py) 导入成功")
except ImportError as e:
    print(f"⚠️ app.py 导入失败: {e}")
    ArtForgeApp = None

# 初始化技能管理器
skill_manager.scan()

# ==========================================
# 3. 核心辅助函数：自动保存图片
# ==========================================
def _save_image_automatically(image: Image.Image, prefix: str = "artforge") -> str:
    """
    自动保存图片到 output 目录。
    优先使用 forgecore 的 Paths.OUTPUT_DIR，否则回退到 PROJECT_ROOT/output。
    """
    if image is None:
        return ""
    try:
        # 尝试获取 forgecore 的输出目录
        save_dir = None
        try:
            from forgecore.config.paths import Paths
            save_dir = Paths.OUTPUT_DIR
        except Exception:
            save_dir = PROJECT_ROOT / "output"
            
        save_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = save_dir / f"{prefix}_{timestamp}.png"
        
        # 确保图片是 RGB/RGBA 模式以便保存
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
            
        image.save(save_path)
        return str(save_path)
    except Exception as e:
        print(f"⚠️ 自动保存图片失败: {e}")
        return ""


# ==========================================
# 4. Tab 1: 东方艺术 (100% 复用 app.py)
# ==========================================
def build_art_forge_tab(app_instance: ArtForgeApp):
    with gr.Tab("🎨 东方艺术"):
        if app_instance:
            app_instance._build_generation_tab()
        else:
            gr.Markdown("❌ app.py 未找到，东方艺术 Tab 不可用")


# ==========================================
# 5. Tab 2: 通用生图 & ControlNet (完整功能 + 自动保存)
# ==========================================
def build_general_gen_tab():
    with gr.Tab("🧍 通用生图 & ControlNet"):
        gr.Markdown("### 🧍 图生图 / ControlNet 工作台")
        gr.Markdown("💡 **核心逻辑**：上传参考图锁定特征，通过提示词引导继续创作。默认使用 Agnes API 图生图，也支持本地 ControlNet 模型。")
        
        with gr.Row():
            with gr.Column(scale=1):
                # 1. 核心：参考图上传 (必须)
                ref_image = gr.Image(label="📎 上传参考图 (Control Source / 图生图底图)", type="pil", height=300)
                
                # 2. 引擎选择 (Agnes API 默认 / 本地模型)
                engine_mode = gr.Radio(
                    choices=[("☁️ Agnes API (图生图)", "agnes"), ("💻 本地模型 (ControlNet)", "local")],
                    value="agnes", 
                    label="生成引擎"
                )
                
                # 本地模型选择
                local_model_dd = gr.Dropdown(
                    choices=[m["name"] for m in ModelRegistry.scan_checkpoints("sd15")],
                    label="本地模型 (SD1.5) - 仅本地引擎生效",
                    value=None,
                    interactive=True
                )

                # 3. 提示词
                gen_prompt = gr.Textbox(label="提示词 (Prompt - 描述你想要的变化/新内容)", value="masterpiece, best quality, detailed face", lines=2)
                gen_neg = gr.Textbox(label="负面提示词 (仅本地模型生效)", value="worst quality, lowres, bad anatomy", lines=1)
                
                # 4. ControlNet / 图生图 控制参数
                with gr.Group():
                    gr.Markdown("#### ️ 控制参数")
                    cn_type_dd = gr.Dropdown(
                        choices=["openpose", "canny", "depth", "lineart", "hed", "无 (纯图生图)"],
                        label="ControlNet 类型 / 参考方式", 
                        value="无 (纯图生图)"
                    )
                    cn_strength = gr.Slider(0.1, 1.0, value=0.6, label="重绘幅度 / ControlNet 强度 (0.1=微调, 1.0=大改)")
                    
                gen_btn = gr.Button(" 开始图生图 / ControlNet 生成", variant="primary", size="lg")
                
            with gr.Column(scale=1):
                gen_out = gr.Image(label="生成结果", type="pil", height=400)
                gen_log = gr.Textbox(label="生成日志", lines=10)

        # 生成逻辑
        def run_img2img(ref_img, mode, model_name, prompt, negative, cn_type, strength):
            logs = [" 启动图生图 / ControlNet 流水线..."]
            
            if ref_img is None:
                return None, "❌ 必须上传参考图！图生图/ControlNet 需要底图来锁定特征。"

            try:
                final_image = None
                
                # ==========================================
                # 路径 A: Agnes API 图生图 (默认)
                # ==========================================
                if mode == "agnes":
                    logs.append(f"☁️ 使用 Agnes API 图生图")
                    logs.append(f"📎 参考图尺寸: {ref_img.size}")
                    
                    from gui.common import load_env_config
                    config = load_env_config()
                    engine = create_engine("agnes", config)
                    
                    try:
                        if hasattr(engine, 'image_to_image'):
                            logs.append("🔄 调用 engine.image_to_image...")
                            final_image = engine.image_to_image(
                                prompt=prompt, 
                                image=ref_img,
                                strength=strength,
                                width=768, height=1024
                            )
                        else:
                            logs.append("️ 引擎无 image_to_image，降级为文生图")
                            final_image = engine.generate_single(prompt=prompt, width=768, height=1024)
                    except TypeError:
                        final_image = engine.image_to_image(prompt=prompt, images=[ref_img], strength=strength)
                        
                    logs.append("✅ Agnes API 图生图完成")

                # ==========================================
                # 路径 B: 本地模型 ControlNet
                # ==========================================
                else:
                    if not model_name:
                        return None, "❌ 选择本地引擎时，必须选择本地模型。"
                    
                    all_models = ModelRegistry.scan_checkpoints("sd15")
                    model_obj = next((m for m in all_models if m["name"] == model_name), None)
                    if not model_obj:
                        return None, "❌ 找不到模型路径"
                    model_path = model_obj["absolute_path"]
                    logs.append(f" 本地模型: {model_name}")

                    if cn_type and cn_type != "无 (纯图生图)":
                        logs.append(f"🎛️ 调用本地 ControlNet Pipeline (类型: {cn_type}, 强度: {strength})")
                        res = skill_manager.run(
                            "controlnet", action="generate", image=ref_img, prompt=prompt,
                            negative_prompt=negative, model_path=model_path,
                            controlnet_type=cn_type, controlnet_conditioning_scale=strength
                        )
                    else:
                        logs.append(f"🖼️ 调用本地图生图 (重绘幅度: {strength})")
                        res = skill_manager.run(
                            "controlnet", action="generate", image=ref_img, prompt=prompt,
                            negative_prompt=negative, model_path=model_path,
                            controlnet_type="canny", controlnet_conditioning_scale=0.0, strength=strength
                        )

                    if res.get("status") == "success":
                        out_path = res["result"].get("output_path")
                        if out_path and Path(out_path).exists():
                            final_image = Image.open(out_path)
                            logs.append(f"✅ 本地生成成功")
                        elif "image" in res["result"]:
                            final_image = res["result"]["image"]
                    else:
                        logs.append(f"❌ 本地生成失败: {res.get('error')}")

                # ==========================================
                # 🆕 核心：自动保存图片
                # ==========================================
                if final_image is not None:
                    save_path = _save_image_automatically(final_image, prefix="img2img")
                    if save_path:
                        logs.append(f"💾 图片已自动保存: {save_path}")
                    return final_image, "\n".join(logs)
                else:
                    return None, "\n".join(logs) + "\n❌ 未生成有效图片"

            except Exception as e:
                import traceback
                return None, f"❌ 执行出错: {str(e)}\n{traceback.format_exc()}"

        gen_btn.click(
            fn=run_img2img,
            inputs=[ref_image, engine_mode, local_model_dd, gen_prompt, gen_neg, cn_type_dd, cn_strength],
            outputs=[gen_out, gen_log]
        )


# ==========================================
# 6. Tab 3: 技能中心 (90 Skills 动态调度)
# ==========================================
def build_skill_hub_tab():
    with gr.Tab("🛠️ 技能中心 (90 Skills)"):
        gr.Markdown("###  ForgeCore 全局技能调度器")
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
            logs = [f"🚀 执行: {skill_name}"]
            try:
                kwargs = json.loads(params_json) if params_json.strip() else {}
                result = skill_manager.run(skill_name, **kwargs)
                if result.get("status") == "success":
                    logs.append("✅ 成功")
                else:
                    logs.append(f"❌ 失败: {result.get('error')}")
                return "\n".join(logs), result
            except Exception as e:
                return f" 错误: {e}", {}

        run_btn.click(fn=execute_skill, inputs=[skill_dd, params_input], outputs=[log_output, result_output])


# ==========================================
# 7. 构建主 GUI
# ==========================================
def build_unified_gui():
    app = ArtForgeApp() if ArtForgeApp else None
    
    with gr.Blocks(title="ArtForge Ultimate", theme=gr.themes.Soft()) as demo:
        with gr.Row():
            gr.Markdown("#  ArtForge Ultimate")
            gr.Markdown(f"**状态**: 🟢 ForgeCore 就绪 | **技能**: {len(skill_manager.list_skills())} 个")
            
        with gr.Tabs():
            build_art_forge_tab(app)
            build_general_gen_tab()
            build_skill_hub_tab()

    return demo

if __name__ == "__main__":
    demo = build_unified_gui()
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, inbrowser=True)