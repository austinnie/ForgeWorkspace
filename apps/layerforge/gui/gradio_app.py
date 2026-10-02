# apps/layerforge/gui/gradio_app.py (极简壳化版)
import sys
import gradio as gr
from pathlib import Path

# ==========================================
# 1. 路径注入 (核心修复：注入项目根目录)
# ==========================================
# 当前文件: E:\SD_OpenVINO\ForgeWorkspace\apps\layerforge\gui\gradio_app.py
APP_ROOT = Path(__file__).resolve().parent.parent  # 指向 apps/layerforge
PROJECT_ROOT = APP_ROOT.parent.parent              # 指向 ForgeWorkspace (项目根目录)

# 🔥 关键：必须把项目根目录加入 sys.path，才能 import forgecore
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    

# 加载全局 .env 环境变量
ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except ImportError:
        pass
        
CORE_PATH = APP_ROOT.parent.parent / "forgecore"
sys.path.insert(0, str(APP_ROOT))
sys.path.insert(0, str(CORE_PATH))

# ==========================================
# 2. 直接复用 ForgeCore (现在不会报错了)
# ==========================================
from forgecore.prompt.composer import PromptComposer
from forgecore.engines import create_engine
from forgecore.post_process import AgingProcessor, SealGenerator


# ==========================================
# 3. 极简预设加载器 (直接读 shared_assets)
# ==========================================
# LayerForge 应该改为：
PRESETS_DIR = PROJECT_ROOT / "shared_assets" / "presets_by_app" / "sketch_forge"
# (因为 LayerForge 的 config.py 里已经指向了 sketch_forge)

def load_presets():
    presets = []
    if ASSETS_PATH.exists():
        for f in ASSETS_PATH.rglob("*.py"):
            if not f.name.startswith("_") and f.name != "__init__.py":
                presets.append(f.stem) # 用文件名作为预设名
    return presets
    
# 引擎：复用统一 API 网关
from forgecore.engines import create_engine

# 后处理：复用统一做旧/印章/题词/水印
from forgecore.post_process.aging_processor import AgingProcessor
from forgecore.post_process.seal_generator import SealGenerator
from forgecore.post_process.watermark import WatermarkProcessor

# ==========================================
# 3. 预设加载 (直接读取 shared_assets)
# ==========================================
def load_unified_presets():
    """直接复用共享资产库，App 层不存任何预设文件"""
    presets_dir = CORE_PATH.parent / "shared_assets" / "presets_unified"
    # 这里可以调用 forgecore 提供的预设扫描工具，或极简实现
    # 假设 forgecore 有 PresetManager，或者直接返回分类字典
    return {"东方美学": ["水墨山水", "工笔花鸟"], "西方古典": ["油画", "雕塑"]} 

presets_map = load_unified_presets()

# ==========================================
# 4. 核心生成逻辑 (纯壳：只组装参数，不写业务)
# ==========================================
def generate_shell(preset_name, engine_name, layer_overrides, use_aging, use_seal):
    logs = []
    
    # 1. 复用 ForgeCore 组合器
    composer = PromptComposer()
    composer.apply_preset(preset_name) # 基盘自动处理 6 层拼接和 Token 截断
    composer.apply_overrides(layer_overrides) # 应用 UI 上的微调
    prompt, negative = composer.compose()
    logs.append(f"✅ 提示词就绪: {prompt[:50]}...")

    # 2. 复用 ForgeCore 引擎
    engine = create_engine(engine_name)
    image = engine.generate_single(prompt=prompt, negative=negative, width=1024, height=1024)
    logs.append(f"✅ 引擎 {engine_name} 出图完成")

    # 3. 复用 ForgeCore 后处理
    if use_aging:
        image = AgingProcessor().apply(image.convert("RGB"), texture="xuan_paper")
        logs.append("📜 做旧完成")
    if use_seal:
        image = SealGenerator().apply_scheme(image, "東方藝術", scheme="default")
        logs.append("🔴 印章完成")

    return image, "\n".join(logs)

# ==========================================
# 5. 极简 UI (只负责展示和传参)
# ==========================================
with gr.Blocks(title="LayerForge (Thin Shell)") as demo:
    gr.Markdown("# 🎨 LayerForge · 纯壳应用 (基于 ForgeCore)")
    
    with gr.Row():
        with gr.Column():
            preset_dd = gr.Dropdown(choices=["水墨山水", "油画"], label="预设")
            engine_dd = gr.Dropdown(choices=["agnes", "pollinations", "freeapi"], label="引擎", value="freeapi")
            # LayerForge 特色的分层微调
            subj_i = gr.Textbox(label="Subject (主体覆盖)")
            scene_i = gr.Textbox(label="Scene (场景覆盖)")
            
            with gr.Row():
                use_aging_cb = gr.Checkbox(label="做旧")
                use_seal_cb = gr.Checkbox(label="印章")
                
            btn = gr.Button("🚀 生成", variant="primary")
            
        with gr.Column():
            img_out = gr.Image(label="结果")
            log_out = gr.Textbox(label="日志")

    # 事件绑定：UI 直接把参数扔给 Shell 函数
    btn.click(
        fn=generate_shell, 
        inputs=[preset_dd, engine_dd, {"subject": subj_i, "scene": scene_i}, use_aging_cb, use_seal_cb], 
        outputs=[img_out, log_out]
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True)