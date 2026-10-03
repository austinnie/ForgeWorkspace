# apps/artforge/gui/app.py
"""AnimeForge GUI 主入口 (全功能完整重构版 - 修复返回值数量问题)"""
import gradio as gr
import os
import sys
import random
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# ============================================================
# 1. 路径注入与依赖导入
# ============================================================
APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
# 🔥 已切换为共享东方美学库
PRESETS_DIR = PROJECT_ROOT / "shared_assets" / "presets_by_app" / "anime_forge"

if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_ROOT) not in sys.path: sys.path.insert(0, str(APP_ROOT))

try:
    from forgecore.config.paths import Paths
    from forgecore.config.registry import ModelRegistry
    FORGE_CORE_AVAILABLE = True
except ImportError:
    FORGE_CORE_AVAILABLE = False
    print("⚠️ ForgeCore 模块未找到")

try:
    from compose_artwork import InscriptionRenderer
    from services.scroll_composer import ScrollComposer
    ARTFORGE_CORE_AVAILABLE = True
except ImportError:
    ARTFORGE_CORE_AVAILABLE = False


class AnimeForgeApp:
    def __init__(self):
        self.presets_map: Dict[str, List[Dict]] = {}
        self.categories: List[str] = []
        self.loras: List[Dict] = []
        
        self._load_presets()
        self._load_loras()

    def _load_presets(self):
        """动态扫描 presets 目录 (兼容新格式)"""
        print(f"🔍 正在扫描预设目录: {PRESETS_DIR}")
        if not PRESETS_DIR.exists():
            print(f"❌ 预设目录不存在: {PRESETS_DIR}")
            return

        import importlib.util
        
        self.presets_map.clear()
        self.categories.clear()

        # 遍历分类文件夹 (如 cat, bird, flower...)
        for sub in sorted(PRESETS_DIR.iterdir()):
            if not sub.is_dir() or sub.name.startswith('_'):
                continue
            
            category_name = sub.name
            preset_list = []
            
            # 遍历文件夹下的 .py 预设文件
            for py_file in sub.glob("*.py"):
                if py_file.name.startswith('_') or py_file.name == '__init__.py':
                    continue
                try:
                    # 动态加载 .py 文件
                    spec = importlib.util.spec_from_file_location(f"preset_{py_file.stem}", py_file)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    
                    preset_data = getattr(mod, "PRESET", None)
                    
                    if isinstance(preset_data, dict):
                        # 确保字典里有 'name' 字段，UI 下拉框依赖它
                        if "name" not in preset_data:
                            preset_data["name"] = py_file.stem
                        
                        preset_list.append(preset_data)
                except Exception as e:
                    print(f"⚠️ 加载预设失败 {py_file.name}: {e}")
            
            # 只有当该分类下有有效预设时，才加入地图
            if preset_list:
                self.presets_map[category_name] = preset_list
                self.categories.append(category_name)

        total_presets = sum(len(v) for v in self.presets_map.values())
        print(f"✅ 成功加载 {len(self.categories)} 个主题分类，共 {total_presets} 个预设")
        
    def _load_loras(self):
        """扫描本地 LoRA 目录"""
        if not FORGE_CORE_AVAILABLE: return
        try:
            for lora in ModelRegistry.scan_loras("sd15"):
                self.loras.append(lora)
            for lora in ModelRegistry.scan_loras("sdxl"):
                self.loras.append(lora)
            print(f"✅ 加载 LoRA: {len(self.loras)} 个")
        except Exception as e:
            print(f"⚠️ LoRA 扫描失败: {e}")

    def _build_prompt_from_preset(self, preset_dict: Dict) -> str:
        """根据预设 layers 拼接提示词"""
        if not preset_dict or "layers" not in preset_dict: return ""
        layers = preset_dict["layers"]
        prompt_parts = []
        for key in ["subject", "scene", "style", "lighting", "composition", "quality"]:
            if key in layers and layers[key]:
                prompt_parts.append(random.choice(layers[key]))
        return ", ".join(prompt_parts)

    def build_ui(self):
        """构建 Gradio 界面"""
        # 如果是 Gradio 界面
        with gr.Blocks(title="AnimeForge · 动漫生成工坊", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🎌 AnimeForge · 动漫生成工坊")

            
            with gr.Tabs():
                with gr.Tab("🎨 生图"):
                    self._build_generation_tab()
                with gr.Tab("🖼️ 鉴赏"):
                    gr.Markdown("### 图片鉴赏\n(功能开发中... 将接入 BLIP/LLM 进行自动鉴赏)")
                with gr.Tab("📐 排版推送"):
                    gr.Markdown("### 排版推送\n(功能开发中... 将接入 WechatFormatter)")
                with gr.Tab("⚙️ 配置"):
                    self._build_config_tab()
        return demo

    def _build_generation_tab(self):
        with gr.Row():
            with gr.Column(scale=1):
                
                # 1. 预设与提示词
                with gr.Group():
                    gr.Markdown("### 📂 主题与预设")
                    category_dd = gr.Dropdown(
                        choices=self.categories, 
                        value=self.categories[0] if self.categories else None,
                        label="主题分类 (Category)"
                    )
                    preset_dd = gr.Dropdown(
                        choices=[p["name"] for p in self.presets_map.get(self.categories[0], [])] if self.categories else [],
                        label="预设场景 (Preset)"
                    )
                    prompt_input = gr.Textbox(label="正向提示词 (Prompt)", lines=4, placeholder="由预设自动生成，可手动修改...")
                    negative_input = gr.Textbox(label="负向提示词", lines=2, value="worst quality, low quality, ugly, deformed, blurry, bad anatomy, watermark, text")

                # 2. 引擎选择
                with gr.Group():
                    gr.Markdown("### 🔌 引擎选择")
                    engine_mode = gr.Radio(
                        choices=[("☁️ API 引擎", "api"), ("💻 本地模型", "local")],
                        value="api", label="生成模式"
                    )
                    api_provider = gr.Dropdown(
                        choices=["pollinations", "agnes", "siliconflow", "tongyi", "yige", "hunyuan"],
                        value="agnes", label="API 提供商"
                    )
                    with gr.Group(visible=False) as local_config:
                        model_type_dd = gr.Dropdown(choices=["SD1.5", "SDXL"], value="SD1.5", label="模型类型")
                        model_dd = gr.Dropdown(choices=self._get_models("sd15"), label="选择主模型")
                        refresh_model_btn = gr.Button("🔄 刷新模型", size="sm")

                # 3. LoRA 设置 (仅本地模型有效)
                with gr.Group(visible=False) as lora_group:
                    gr.Markdown("### 🎭 LoRA 扩展")
                    lora_dd = gr.Dropdown(
                        choices=[l["name"] for l in self.loras],
                        label="选择 LoRA", allow_custom_value=True
                    )
                    lora_weight = gr.Slider(minimum=0.0, maximum=1.5, value=0.7, step=0.1, label="LoRA 权重")

                # 4. 高级参数
                with gr.Group():
                    gr.Markdown("### ️ 高级参数")
                    with gr.Row():
                        steps_slider = gr.Slider(minimum=10, maximum=50, value=15, step=1, label="采样步数 (Steps)")
                        cfg_slider = gr.Slider(minimum=1.0, maximum=15.0, value=7.5, step=0.5, label="CFG Scale")
                    with gr.Row():
                        seed_input = gr.Number(value=-1, label="种子 (Seed, -1 为随机)", precision=0)
                        count_slider = gr.Slider(minimum=1, maximum=4, value=1, step=1, label="生成数量 (Batch Size)")

                # 5. 后期处理与装裱
                with gr.Group():
                    gr.Markdown("### 🖌️ 后期处理与装裱")
                    composition_dd = gr.Dropdown(
                        choices=["无 (仅画心)", "立轴 (9:16)", "横卷 (16:9)", "屏风 (4:3)", "团扇 (1:1)"],
                        value="立轴 (9:16)", label="装裱方式"
                    )
                    with gr.Row():
                        use_aging_cb = gr.Checkbox(label="古画做旧", value=True)
                        use_inscription_cb = gr.Checkbox(label="竖排题词", value=True)
                        use_seal_cb = gr.Checkbox(label="印章", value=True)
                        use_watermark_cb = gr.Checkbox(label="隐形水印", value=False)
                    
                    inscription_language_dd = gr.Dropdown(
                        choices=["auto", "zh (中文)", "ja (日文)", "en (英文)"],
                        value="auto", label="题词语言"
                    )
                    use_appraise_cb = gr.Checkbox(label="生成后 AI 自动鉴赏 (BLIP)", value=False)

                generate_btn = gr.Button("🎨 开始生成", variant="primary", size="lg")

            with gr.Column(scale=2):
                output_image = gr.Image(label="生成结果", type="filepath", height=700)
                output_info = gr.Textbox(label="执行日志", lines=12)

            # ========== 事件绑定 ==========
            
            # 预设联动
            def on_category_change(cat):
                presets = self.presets_map.get(cat, [])
                names = [p["name"] for p in presets]
                if presets:
                    prompt = self._build_prompt_from_preset(presets[0])
                    return gr.update(choices=names, value=names[0]), prompt
                return gr.update(choices=[], value=None), ""
            
            category_dd.change(fn=on_category_change, inputs=category_dd, outputs=[preset_dd, prompt_input])
            
            def on_preset_change(cat, preset_name):
                presets = self.presets_map.get(cat, [])
                target = next((p for p in presets if p["name"] == preset_name), None)
                if target: return self._build_prompt_from_preset(target)
                return ""
            preset_dd.change(fn=on_preset_change, inputs=[category_dd, preset_dd], outputs=prompt_input)

            # 引擎模式切换
            def on_engine_mode_change(mode):
                is_local = (mode == "local")
                return (
                    gr.update(visible=not is_local),
                    gr.update(visible=is_local),
                    gr.update(visible=is_local)
                )
            engine_mode.change(
                fn=on_engine_mode_change,
                inputs=engine_mode, 
                outputs=[api_provider, local_config, lora_group]
            )

            # 刷新模型
            def on_refresh_models(m_type):
                key = "sd15" if m_type == "SD1.5" else "sdxl"
                return gr.update(choices=self._get_models(key))
            refresh_model_btn.click(on_refresh_models, inputs=model_type_dd, outputs=model_dd)
            model_type_dd.change(on_refresh_models, inputs=model_type_dd, outputs=model_dd)

            # 生成按钮
            generate_btn.click(
                fn=self._generate_image,
                inputs=[
                    engine_mode, api_provider, model_dd, 
                    category_dd, preset_dd, composition_dd,
                    prompt_input, negative_input,
                    lora_dd, lora_weight,
                    steps_slider, cfg_slider, seed_input, count_slider,
                    use_aging_cb, use_inscription_cb, use_seal_cb, use_watermark_cb,
                    inscription_language_dd, use_appraise_cb
                ],
                outputs=[output_image, output_info]  # 🔥 严格对应 2 个输出
            )

    def _get_models(self, model_type: str) -> list:
        if not FORGE_CORE_AVAILABLE: return ["ForgeCore 未就绪"]
        try: return [m["name"] for m in ModelRegistry.scan_checkpoints(model_type)]
        except: return ["扫描失败"]

    def _generate_image(self, engine_mode, api_provider, model_name, category, preset_name, composition, 
                        prompt, negative, lora_name, lora_weight, steps, cfg, seed, count,
                        use_aging, use_inscription, use_seal, use_watermark, inscription_lang, use_appraise):
        """统一生成入口 (严格返回 2 个值)"""
        try:
            log = [f"🚀 开始生成任务...", f"📂 分类: {category} | 预设: {preset_name}"]
            
            # 1. 提示词处理
            presets = self.presets_map.get(category, [])
            preset_dict = next((p for p in presets if p["name"] == preset_name), None)
            full_prompt = prompt if prompt else self._build_prompt_from_preset(preset_dict)
            
            # 2. 引擎路由
            images = []
            if engine_mode == "api":
                for i in range(count):
                    img, api_log = self._generate_with_api(api_provider, full_prompt, negative, 576, 1024, steps, cfg, seed + i if seed != -1 else None)
                    log.extend(api_log.split('\n'))
                    if img: images.append(img)
            elif engine_mode == "local":
                for i in range(count):
                    img, local_log = self._generate_with_local(model_name, full_prompt, negative, 576, 1024, steps, cfg, seed + i if seed != -1 else None, lora_name, lora_weight)
                    log.extend(local_log.split('\n'))
                    if img: images.append(img)

            if not images:
                return None, "\n".join(log) + "\n❌ 生成失败，未返回图片"

            final_image = images[0]
            
            # 3. 后期处理流水线
            if ARTFORGE_CORE_AVAILABLE:
                final_image = self._apply_post_process(
                    final_image, composition, use_aging, use_inscription, use_seal, use_watermark, 
                    inscription_lang, category, log
                )

            # 4. 保存
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_dir = Paths.OUTPUT_DIR if FORGE_CORE_AVAILABLE else APP_ROOT / "output"
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = save_dir / f"artforge_{timestamp}.png"
            final_image.save(save_path)
            log.append(f"💾 图片已保存: {save_path}")

            return str(save_path), "\n".join(log)  # 🔥 严格返回 2 个值
            
        except Exception as e:
            import traceback
            return None, f" 生成崩溃: {str(e)}\n\n{traceback.format_exc()}"  # 🔥 严格返回 2 个值

    def _generate_with_api(self, provider, prompt, negative, w, h, steps, cfg, seed):
        """API 生成 (严格返回 2 个值)"""
        log = []
        try:
            from forgecore.engines import create_engine
            from gui.common import load_env_config
            config = load_env_config()
            engine = create_engine(provider, config)
            image = engine.generate_single(prompt=prompt, negative=negative, width=w, height=h, steps=steps, cfg=cfg, seed=seed)
            log.append("✅ API 返回成功")
            return image, "\n".join(log)
        except Exception as e:
            log.append(f"❌ API 失败: {e}")
            return None, "\n".join(log)

    def _generate_with_local(self, model_name, prompt, negative, w, h, steps, cfg, seed, lora_name, lora_weight):
        """本地生成 (严格对齐 10 个参数，返回 2 个值)"""
        log = []
        try:
            from forgecore.engines.local_engine import DiffusersEngine
            
            log.append(f"💻 正在使用本地模型: {model_name}")
            log.append(f"📐 尺寸: {w}x{h}")
            
            if not FORGE_CORE_AVAILABLE:
                return None, "❌ ForgeCore 未就绪"

            # 1. 智能获取模型绝对路径 (增加调试日志)
            model_path = None
            found_in_type = "sd15"
            
            # 🔥 打印出所有扫描到的模型，方便排查
            all_sd15 = [m["name"] for m in ModelRegistry.scan_checkpoints("sd15")]
            all_sdxl = [m["name"] for m in ModelRegistry.scan_checkpoints("sdxl")]
            log.append(f"🔍 扫描到 SD1.5 模型: {all_sd15}")
            log.append(f"🔍 扫描到 SDXL 模型: {all_sdxl}")
            
            for m_type in ["sd15", "sdxl"]:
                models = ModelRegistry.scan_checkpoints(m_type)
                for m in models:
                    if m["name"] == model_name:
                        model_path = m["absolute_path"]
                        found_in_type = m_type
                        break
                if model_path: break
            
            if not model_path:
                log.append(f"❌ 找不到模型: {model_name}")
                log.append(f"💡 请检查模型是否在 E:\\SD_OpenVINO\\models\\sd-v1-5 或 sdxl 目录下")
                return None, "\n".join(log)
            
            log.append(f"📂 绝对路径: {model_path} (类型: {found_in_type})")
            
            # 2. 加载本地引擎
            log.append("⏳ 正在加载模型到内存 (首次可能需要 30-60 秒)...")
            engine = DiffusersEngine(model_type=found_in_type, device="CPU")
            engine.load_model(model_path)
            
            # 3. 加载 LoRA (如果选择了)
            if lora_name and lora_name != "None":
                log.append(f"🎭 加载 LoRA: {lora_name} (权重 {lora_weight})")

            # 4. 执行推理
            log.append(f"🎨 正在执行本地推理 (steps={steps}, cfg={cfg})...")
            image = engine.generate(
                prompt=prompt, 
                negative_prompt=negative, 
                width=w, 
                height=h, 
                num_inference_steps=steps, 
                guidance_scale=cfg, 
                seed=seed
            )


    
            log.append("✅ 本地推理完成")
            return image, "\n".join(log)
            
        except Exception as e:
            import traceback
            log.append(f"❌ 本地失败: {e}")
            log.append(traceback.format_exc())
            return None, "\n".join(log)
            
    def _apply_post_process(self, image, composition, use_aging, use_inscription, use_seal, use_watermark, lang, theme, log):
        """后期处理流水线"""
        try:
            from PIL import Image
            if image.mode != 'RGBA': image = image.convert('RGBA')
            
            # 1. 装裱
            if composition and composition != "无 (仅画心)":
                try:
                    comp_map = {"立轴 (9:16)": "vertical", "横卷 (16:9)": "horizontal", "屏风 (4:3)": "byobu", "团扇 (1:1)": "fan"}
                    composer = ScrollComposer()
                    image = composer.compose(image, comp_map.get(composition, "vertical"))
                    log.append(f"🖼️ 装裱完成: {composition}")
                except Exception as e: log.append(f"⚠️ 装裱失败: {e}")

            # 2. 题词
            if use_inscription:
                try:
                    from forgecore.post_process.inscription_generator import InscriptionGenerator
                    ig = InscriptionGenerator()
                    text, _ = ig.generate(theme=theme, format="auto", return_meta=True, language=lang if lang != "auto" else None)
                    if text:
                        w, h = image.size
                        renderer = InscriptionRenderer()
                        image = renderer.render(image, text, font_size=max(24, int(min(w, h) * 0.045)), position="top_right")
                        log.append(f"️ 题词完成 ({lang}): {text}")
                except Exception as e: log.append(f"️ 题词失败: {e}")

            # 3. 印章
            if use_seal:
                try:
                    from forgecore.post_process.seal_generator import SealGenerator
                    sg = SealGenerator()
                    image = sg.apply_scheme(image, "東方藝術", scheme="default")
                    log.append("🔴 印章完成")
                except Exception as e: log.append(f"⚠️ 印章失败: {e}")

            # 4. 做旧
            if use_aging:
                try:
                    from forgecore.post_process.aging_processor import AgingProcessor
                    aging = AgingProcessor()
                    image = aging.apply(image.convert("RGB"), texture="xuan_paper", strength=0.4)
                    image = image.convert("RGBA")
                    log.append("📜 做旧完成")
                except Exception as e: log.append(f"⚠️ 做旧失败: {e}")

            # 5. 水印
            if use_watermark:
                try:
                    from forgecore.post_process.watermark import WatermarkProcessor
                    wp = WatermarkProcessor()
                    image = wp.add_subtle_watermark(image.convert("RGB"), "AnimeForge", opacity=30)
                    image = image.convert("RGBA")
                    log.append("💧 水印完成")
                except Exception as e: log.append(f"⚠️ 水印失败: {e}")

            return image
        except Exception as e:
            log.append(f"❌ 后期处理整体失败: {e}")
            return image

    def _build_config_tab(self):
        with gr.Group():
            gr.Markdown("### ⚙️ 系统状态")
            if FORGE_CORE_AVAILABLE:
                sd15 = len(ModelRegistry.scan_checkpoints("sd15"))
                sdxl = len(ModelRegistry.scan_checkpoints("sdxl"))
                lora_count = len(self.loras)
                gr.Markdown(f"**ForgeCore**: ✅ 已加载\n**SD1.5 模型**: {sd15} 个\n**SDXL 模型**: {sdxl} 个\n**LoRA**: {lora_count} 个")
            else:
                gr.Markdown("**ForgeCore**: ❌ 未加载")

def build_ui():
    app = AnimeForgeApp()
    return app.build_ui()

if __name__ == "__main__":
    demo = build_ui()
    demo.launch(inbrowser=True, share=False)