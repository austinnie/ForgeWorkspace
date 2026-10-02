# apps/layerforge/gui/gradio_app.py
"""LayerForge GUI 主入口 (终极完整修复版 - 参考 ArtForge 架构)"""
import gradio as gr
import os
import sys
import random
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# ==========================================
# 1. 路径注入 (与 ArtForge 完全一致)
# ==========================================
APP_ROOT = Path(__file__).resolve().parents[1]  # apps/layerforge
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # ForgeWorkspace

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# ==========================================
# 2. 导入 ForgeCore 基盘
# ==========================================
try:
    from forgecore.config.paths import Paths
    from forgecore.config.registry import ModelRegistry
    from forgecore.engines import create_engine
    from forgecore.engines.local_engine import DiffusersEngine
    from forgecore.prompt.composer import PromptComposer
    from forgecore.post_process.aging_processor import AgingProcessor
    from forgecore.post_process.seal_generator import SealGenerator
    FORGE_CORE_AVAILABLE = True
except ImportError as e:
    FORGE_CORE_AVAILABLE = False
    print(f"⚠️ ForgeCore 导入失败: {e}")

# ==========================================
# 3. 辅助函数：加载 API 配置 (解决 AGNES_API_KEY 报错的核心)
# ==========================================
def load_env_config() -> dict:
    """从环境变量获取所有 API 配置 (参考 ArtForge)"""
    return {
        "AGNES_API_KEY": os.getenv("AGNES_API_KEY", ""),
        "AGNES_BASE_URL": os.getenv("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1"),
        "AGNES_IMAGE_MODEL": os.getenv("AGNES_IMAGE_MODEL", "agnes-image-2.1-flash"),
        "POLLINATIONS_MODEL": os.getenv("POLLINATIONS_MODEL", "flux"),
        "FREEAPI_MODEL": os.getenv("FREEAPI_MODEL", "grok-imagine-image-lite"),
    }

# ==========================================
# 4. 预设扫描与加载器
# ==========================================
PRESETS_DIR = PROJECT_ROOT / "shared_assets" / "presets_by_app" / "sketch_forge"
PRESETS_DIR_UNIFIED = PROJECT_ROOT / "shared_assets" / "presets_unified"

def scan_presets() -> List[str]:
    """扫描所有可用预设文件名"""
    presets = []
    for p_dir in [PRESETS_DIR, PRESETS_DIR_UNIFIED]:
        if p_dir.exists():
            for f in p_dir.rglob("*.py"):
                if not f.name.startswith("_") and f.name != "__init__.py":
                    name = f.stem
                    if name not in presets:
                        presets.append(name)
    return presets if presets else ["dragon_sketch"] # 兜底

def load_preset_layers(preset_name: str) -> dict:
    """加载指定预设的 layers 字典"""
    for p_dir in [PRESETS_DIR, PRESETS_DIR_UNIFIED]:
        if p_dir.exists():
            for f in p_dir.rglob(f"{preset_name}.py"):
                try:
                    spec = importlib.util.spec_from_file_location(preset_name, f)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'LAYERS'):
                        return module.LAYERS
                    elif hasattr(module, 'PRESET') and isinstance(module.PRESET, dict) and 'layers' in module.PRESET:
                        return module.PRESET['layers']
                except Exception as e:
                    pass
    # 兜底 layers
    return {
        "subject": ["a beautiful landscape"],
        "scene": ["outdoor"],
        "style": ["masterpiece, best quality"],
        "lighting": ["natural light"],
        "view": ["wide angle"],
        "quality": ["4k resolution"]
    }

# ==========================================
# 5. LayerForgeApp 核心类
# ==========================================
class LayerForgeApp:
    def __init__(self):
        self.all_presets = scan_presets()
        self.local_models = []
        
        if FORGE_CORE_AVAILABLE:
            try:
                sd15 = ModelRegistry.scan_checkpoints("sd15")
                sdxl = ModelRegistry.scan_checkpoints("sdxl")
                self.local_models = [m["name"] for m in sd15 + sdxl]
            except Exception as e:
                print(f"⚠️ 扫描本地模型失败: {e}")

    def build_ui(self):
        with gr.Blocks(title="LayerForge (Thin Shell)") as demo:
            gr.Markdown("# 🎨 LayerForge · 纯壳应用 (支持 API + 本地模型)")
            
            with gr.Row():
                with gr.Column():
                    preset_dd = gr.Dropdown(
                        choices=self.all_presets, 
                        label="预设 (来自 shared_assets)", 
                        value=self.all_presets[0] if self.all_presets else None
                    )
                    
                    # 引擎模式选择
                    engine_mode = gr.Radio(
                        choices=[("☁️ API 引擎", "api"), (" 本地模型", "local")],
                        value="api", label="生成模式"
                    )
                    
                    api_provider = gr.Dropdown(
                        choices=["freeapi", "pollinations", "agnes", "siliconflow"],
                        label="API 提供商", value="freeapi"
                    )
                    
                    local_model_dd = gr.Dropdown(
                        choices=self.local_models,
                        label="本地模型 (SD1.5/SDXL)",
                        value=self.local_models[0] if self.local_models else None,
                        visible=False
                    )
                    
                    # 联动逻辑
                    def on_mode_change(mode):
                        if mode == "local":
                            return gr.update(visible=True), gr.update(visible=False)
                        else:
                            return gr.update(visible=False), gr.update(visible=True)
                    engine_mode.change(fn=on_mode_change, inputs=engine_mode, outputs=[local_model_dd, api_provider])

                    subject_i = gr.Textbox(label="主体微调 (可选)")
                    scene_i = gr.Textbox(label="场景微调 (可选)")
                    
                    # 🔥 核心修复：必须在这里定义 steps_slider 和 cfg_slider！
                    steps_slider = gr.Slider(minimum=10, maximum=50, value=20, step=1, label="采样步数 (Steps)")
                    cfg_slider = gr.Slider(minimum=1.0, maximum=15.0, value=7.0, step=0.5, label="提示词相关性 (CFG)")
                    
                    with gr.Row():
                        aging_cb = gr.Checkbox(label="做旧", value=False)
                        seal_cb = gr.Checkbox(label="印章", value=False)
                        
                    btn = gr.Button("🚀 生成", variant="primary")
                    
                with gr.Column():
                    img_out = gr.Image(label="结果")
                    log_out = gr.Textbox(label="日志", lines=10)

            # 🔥 注意：inputs 列表的顺序必须和 generate_shell 的参数顺序完全一致！
            btn.click(
                fn=self.generate_shell,
                inputs=[engine_mode, api_provider, local_model_dd, preset_dd, subject_i, scene_i, steps_slider, cfg_slider, aging_cb, seal_cb],
                outputs=[img_out, log_out]
            )
        return demo

    def generate_shell(self, engine_mode, api_provider, local_model_name, preset_name, subject, scene, steps, cfg, use_aging, use_seal):
        logs = []
        try:
            # 1. 加载预设与提示词组合
            layers = load_preset_layers(preset_name)
            if subject: layers["subject"] = [subject]
            if scene: layers["scene"] = [scene]
            
            # 🔥 核心修复：必须传入 layers，并使用 max_tokens=75 防止 CLIP 索引错误
            composer = PromptComposer(layers=layers)
            prompt = composer.compose_random(max_tokens=75)
            
            negative_layers = layers.get("negative", [])
            negative = ", ".join(negative_layers) if negative_layers else "worst quality, low quality, ugly, deformed, blurry, bad anatomy, watermark, text, signature"
            
            logs.append(f"✅ 提示词组合完成 (Steps: {steps}, CFG: {cfg})")
            
            # 2. 引擎调度 (API vs 本地)
            image = None
            seed = random.randint(1, 2**32 - 1)
            
            if engine_mode == "local":
                if not self.local_models:
                    return None, "❌ 未找到本地模型"
                
                # 查找模型路径和类型
                model_path = None
                model_type = "sd15"
                for m_type in ["sd15", "sdxl"]:
                    models = ModelRegistry.scan_checkpoints(m_type)
                    for m in models:
                        if m["name"] == local_model_name:
                            model_path = m["absolute_path"]
                            model_type = m_type
                            break
                    if model_path: break
                
                if not model_path:
                    return None, f"❌ 找不到模型: {local_model_name}"
                
                # 分辨率自适应
                if model_type == "sdxl":
                    width, height = 1024, 1024
                else:
                    width, height = 512, 768
                    
                logs.append(f"💻 本地模型: {local_model_name} ({model_type}) | 分辨率: {width}x{height}")
                
                # 初始化并加载模型
                engine = DiffusersEngine(model_type=model_type, device="CPU")
                logs.append("⏳ 正在加载模型到内存 (首次需 30-60 秒)...")
                engine.load_model(model_path)
                logs.append("✅ 模型加载完成，开始生成...")
                
                # 🔥 核心修复：DiffusersEngine 的 generate 方法必须用 num_inference_steps 和 guidance_scale
                image = engine.generate(
                    prompt=prompt, 
                    negative_prompt=negative, 
                    width=width, 
                    height=height, 
                    num_inference_steps=steps, 
                    guidance_scale=cfg, 
                    seed=seed
                )
            else:
                logs.append(f"☁️ 正在使用 API 引擎: {api_provider}")
                config = load_env_config()
                engine = create_engine(api_provider, config=config)
                
                # 🔥 核心修复：API 引擎使用 generate_single，参数名是 steps 和 cfg
                image = engine.generate_single(
                    prompt=prompt, 
                    negative=negative, 
                    width=1024, 
                    height=1024, 
                    steps=steps, 
                    cfg=cfg, 
                    seed=seed
                )
                
            logs.append(f"✅ 引擎出图完成")
            
            # 3. 后处理流水线
            if use_aging:
                image = AgingProcessor().apply(image.convert("RGB"))
                logs.append("📜 做旧完成")
            if use_seal:
                image = SealGenerator().apply_scheme(image, "東方藝術")
                logs.append("🔴 印章完成")
                
            return image, "\n".join(logs)
            
        except Exception as e:
            import traceback
            return None, f"❌ 生成失败: {e}\n\n{traceback.format_exc()}"

def build_ui():
    app = LayerForgeApp()
    return app.build_ui()

if __name__ == "__main__":
    demo = build_ui()
    demo.launch(inbrowser=True, share=False)