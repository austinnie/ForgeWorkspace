"""ArtForge GUI 主入口 (重构版 - Tab 拆分)"""
import os
import sys
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import gradio as gr
from PIL import Image

# 🔥 通用预设引擎
try:
    from forgecore.prompt import PresetEngine
    PRESET_ENGINE_AVAILABLE = True
except ImportError:
    PRESET_ENGINE_AVAILABLE = False
    print("⚠️ PresetEngine 未找到")

# ============================================================
# 🎨 个性化配置
# ============================================================
WATERMARK_TEXT = "东方艺术"
ARTIST_NAME = "东方艺术"

INSCRIPTION_THEME_MAP = {
    "tengu": "天狗",
    "kappa": "河童",
    "kitsune": "九尾狐",
    "yuki_onna": "雪女",
    "oni": "鬼",
    "hyakki_yagyo": "百鬼夜行",
    "dunhuang": "飞天",
    "feitian": "飞天",
    "tang_beauty": "唐仕女",
    "default": "通用",
}

# ============================================================
# 路径注入
# ============================================================
APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

try:
    from forgecore.config.paths import Paths
    from forgecore.config.registry import ModelRegistry
    from forgecore.engines import create_engine
    from forgecore.skills.manager import skill_manager
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


class ArtForgeApp:
    def __init__(self):
        self.loras: List[Dict] = []
        
        # OrcaRouter 当前选中的模型（从 UI 同步）
        self.orcarouter_model: str = "openai/gpt-image-1"

        # 预设库根目录
        self.PRESETS_BASE = PROJECT_ROOT / "shared_assets" / "presets_by_app"

        # 通用预设引擎
        if PRESET_ENGINE_AVAILABLE:
            self.preset_engine = PresetEngine(
                presets_base=self.PRESETS_BASE,
                default_layers=None,
            )
        else:
            self.preset_engine = None

        # 当前选中的库 / 分类 / 预设
        self.current_lib = "oriental_forge"
        self.current_category: Optional[str] = None
        self.current_preset: Optional[str] = None

        self.available_libs = (
            self.preset_engine.list_libraries() if self.preset_engine else []
        )
        if self.current_lib not in self.available_libs and self.available_libs:
            self.current_lib = self.available_libs[0]

        self.categories = (
            self.preset_engine.list_categories(self.current_lib)
            if self.preset_engine else []
        )

        self._load_loras()

        try:
            from forgecore.templates.manager import TemplateManager
            self.template_manager = TemplateManager(
                PROJECT_ROOT / "shared_assets" / "templates" / "sd_gui" / "prompts"
            )
            print(f"✅ JSON 模板加载完成: {len(self.template_manager.categories)} 个分类")
        except Exception as e:
            print(f"⚠️ JSON 模板加载失败: {e}")
            self.template_manager = None

    # ---------- 工具方法 ----------

    def _load_loras(self):
        if not FORGE_CORE_AVAILABLE:
            return
        try:
            for lora in ModelRegistry.scan_loras("sd15"):
                self.loras.append(lora)
            for lora in ModelRegistry.scan_loras("sdxl"):
                self.loras.append(lora)
            print(f"✅ 加载 LoRA: {len(self.loras)} 个")
        except Exception as e:
            print(f"⚠️ LoRA 扫描失败: {e}")

    def _build_prompt_from_preset(self, preset_dict: Dict) -> str:
        if not preset_dict:
            return ""
        if self.preset_engine is not None:
            positive, _ = self.preset_engine.build_prompt(preset_dict)
            return positive
        if "layers" not in preset_dict:
            return ""
        layers = preset_dict["layers"]
        parts = []
        for key in ["subject", "scene", "style", "lighting", "composition", "quality"]:
            if key in layers and layers[key]:
                parts.append(random.choice(layers[key]))
        return ", ".join(parts)

    def _get_models(self, model_type: str) -> list:
        if not FORGE_CORE_AVAILABLE:
            return ["ForgeCore 未就绪"]
        try:
            return [m["name"] for m in ModelRegistry.scan_checkpoints(model_type)]
        except Exception:
            return ["扫描失败"]

    # ---------- UI ----------

    def build_ui(self):
        from apps.artforge.gui.tabs import (
            build_generation_tab,
            build_img2img_tab,
            build_pixel_magic_tab,
            build_skill_hub_tab,
            build_chat_tab,
            build_config_tab,
        )

        with gr.Blocks(title="ArtForge · 东方艺术生成工坊") as demo:
            gr.Markdown("# 🎎 ArtForge · 东方艺术生成工坊")
            with gr.Tabs():
                with gr.Tab("🎨 生图"):
                    build_generation_tab(self)
                with gr.Tab("🖼️ 图生图"):
                    build_img2img_tab(self)
                with gr.Tab("🪄 像素魔法"):
                    build_pixel_magic_tab(self)
                with gr.Tab("🛠️ 技能中心"):
                    build_skill_hub_tab(self)
                with gr.Tab("💬 对话生图"):
                    build_chat_tab(self)
                with gr.Tab("️ 鉴赏与排版"):
                    gr.Markdown("### 图片鉴赏与排版推送\n(功能开发中...)")
                with gr.Tab("⚙️ 配置"):
                    build_config_tab(self)
        return demo

    # ---------- 生成调度 ----------

    def _generate_image(self, engine_mode, api_provider, model_name, category, preset_name, composition,
                        prompt, negative, lora_name, lora_weight, steps, cfg, seed, count,
                        use_aging, aging_strength, aging_texture,
                        use_inscription, inscription_format, inscription_position,
                        use_library_only,
                        use_seal, use_watermark, save_clean_copy, inscription_lang, use_appraise,
                        seal_texture):
        try:
            log = ["🚀 开始生成任务...", f"📂 分类: {category} | 预设: {preset_name}"]

            SCROLL_SIZE_MAP = {
                "立轴 (9:16)": (768, 1360),
                "横卷 (16:9)": (1360, 768),
                "屏风 (4:3)": (1024, 768),
                "团扇 (1:1)": (1024, 1024),
                "无 (仅画心)": (768, 1024),
            }
            width, height = SCROLL_SIZE_MAP.get(composition, (768, 1024))
            log.append(f" 检测到装裱方式 [{composition}]，自动调整生图尺寸为: {width}x{height}")

            preset_dict = (
                self.preset_engine.load_preset(self.current_lib, category, preset_name)
                if self.preset_engine else None
            )
            full_prompt = prompt if prompt else self._build_prompt_from_preset(preset_dict)

            images = []
            if engine_mode == "api":
                for i in range(count):
                    img, api_log = self._generate_with_api(
                        api_provider, full_prompt, negative, width, height, steps, cfg,
                        seed + i if seed != -1 else None,
                    )
                    log.extend(api_log.split('\n'))
                    if img:
                        images.append(img)
            elif engine_mode == "local":
                for i in range(count):
                    img, local_log = self._generate_with_local(
                        model_name, full_prompt, negative, width, height, steps, cfg,
                        seed + i if seed != -1 else None, lora_name, lora_weight,
                    )
                    log.extend(local_log.split('\n'))
                    if img:
                        images.append(img)

            if not images:
                return None, None, "\n".join(log) + "\n❌ 生成失败，未返回图片"

            final_image = images[0]

            if ARTFORGE_CORE_AVAILABLE:
                final_image, clean_image = self._apply_post_process(
                    final_image, composition,
                    use_aging, aging_strength, aging_texture,
                    use_inscription, inscription_lang, inscription_format, inscription_position, use_library_only,
                    use_seal, use_watermark, save_clean_copy,
                    preset_name, category, log,
                    full_prompt, seal_texture,
                )
            else:
                clean_image = None

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_dir = Paths.OUTPUT_DIR if FORGE_CORE_AVAILABLE else APP_ROOT / "output"
            save_dir.mkdir(parents=True, exist_ok=True)

            main_path = None
            clean_path = None

            if final_image:
                main_path = save_dir / f"artforge_{timestamp}.png"
                final_image.save(main_path)
                log.append(f"💾 分享版已保存: {main_path}")

            if clean_image is not None:
                clean_path = save_dir / f"artforge_{timestamp}_clean.png"
                clean_image.save(clean_path)
                log.append(f"🔒 留底版已保存: {clean_path}")

            return (
                str(main_path) if main_path else None,
                str(clean_path) if clean_path else None,
                "\n".join(log),
            )

        except Exception as e:
            import traceback
            return None, None, f"❌ 生成崩溃: {str(e)}\n\n{traceback.format_exc()}"

    def _generate_with_api(self, provider, prompt, negative, w, h, steps, cfg, seed):
        log = []
        try:
            from forgecore.engines import create_engine
            from gui.common import load_env_config
            config = load_env_config()

            # OrcaRouter 使用实例属性中的模型配置
            if provider == "orcarouter":
                config["ORCAROUTER_IMAGE_MODEL"] = self.orcarouter_model
            
            engine = create_engine(provider, config)
            image = engine.generate_single(
                prompt=prompt, negative=negative, width=w, height=h,
                steps=steps, cfg=cfg, seed=seed,
            )
            log.append("✅ API 返回成功")
            return image, "\n".join(log)
        except Exception as e:
            log.append(f"❌ API 失败: {e}")
            return None, "\n".join(log)

    def _generate_with_local(self, model_name, prompt, negative, w, h, steps, cfg, seed, lora_name, lora_weight):
        log = []
        try:
            from forgecore.engines.local_engine import DiffusersEngine
            log.append(f"💻 正在使用本地模型: {model_name}")
            log.append(f"📐 尺寸: {w}x{h}")

            if not FORGE_CORE_AVAILABLE:
                return None, "❌ ForgeCore 未就绪"

            from forgecore.config.model_resolver import resolve_model
            model_obj = resolve_model(model_name)
            model_path = model_obj["absolute_path"] if model_obj else None
            found_in_type = model_obj["type"] if model_obj else "sd15"

            if not model_path:
                log.append(f"❌ 找不到模型: {model_name}")
                return None, "\n".join(log)

            log.append(f"📂 绝对路径: {model_path} (类型: {found_in_type})")
            log.append("⏳ 正在加载模型到内存 (首次可能需要 30-60 秒)...")
            engine = DiffusersEngine(model_type=found_in_type, device="CPU")
            engine.load_model(model_path)

            if lora_name and lora_name != "None":
                log.append(f"🎭 加载 LoRA: {lora_name} (权重 {lora_weight})")

            log.append(f"🎨 正在执行本地推理 (steps={steps}, cfg={cfg})...")
            image = engine.generate(
                prompt=prompt,
                negative_prompt=negative,
                width=w, height=h,
                num_inference_steps=steps,
                guidance_scale=cfg,
                seed=seed,
            )
            log.append("✅ 本地推理完成")
            return image, "\n".join(log)

        except Exception as e:
            import traceback
            log.append(f"❌ 本地失败: {e}")
            log.append(traceback.format_exc())
            return None, "\n".join(log)

    def _apply_post_process(self, image, composition,
                            use_aging, aging_strength, aging_texture,
                            use_inscription, inscription_lang, inscription_format, inscription_position, use_library_only,
                            use_seal, use_watermark, save_clean_copy,
                            preset_name, category, log,
                            context="",
                            seal_texture="flat"):
        try:
            from PIL import Image as _PILImage
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            if use_inscription:
                try:
                    from forgecore.post_process.inscription_generator import InscriptionGenerator
                    from compose_artwork import InscriptionRenderer

                    ig = InscriptionGenerator()
                    backend = "library" if use_library_only else "auto"

                    final_theme = INSCRIPTION_THEME_MAP.get(
                        preset_name,
                        INSCRIPTION_THEME_MAP.get(category, "通用"),
                    )

                    text, _ = ig.generate(
                        theme=final_theme,
                        format=inscription_format,
                        return_meta=True,
                        language=inscription_lang if inscription_lang != "auto" else None,
                        backend=backend,
                        context=context,
                    )

                    if text:
                        w, h = image.size
                        renderer = InscriptionRenderer()
                        image = renderer.render(
                            image, text,
                            font_size=max(24, int(min(w, h) * 0.045)),
                            position=inscription_position,
                        )
                        log.append(f"️ 题词完成 [{inscription_format} @ {inscription_position}] (模式:{backend})")
                    else:
                        log.append("⚠️ 题词生成结果为空")
                except Exception as e:
                    log.append(f"⚠️ 题词失败: {e}")

            if use_seal:
                try:
                    from forgecore.post_process.seal_generator import SealGenerator
                    sg = SealGenerator()
                    image = sg.apply_scheme(image, ARTIST_NAME, scheme="contrast", texture=seal_texture)
                    log.append(f"🔴 印章完成(质感: {seal_texture})")
                except Exception as e:
                    log.append(f"⚠️ 印章失败: {e}")

            if composition and composition != "无 (仅画心)":
                try:
                    comp_map = {
                        "立轴 (9:16)": "vertical",
                        "横卷 (16:9)": "horizontal",
                        "屏风 (4:3)": "byobu",
                        "团扇 (1:1)": "fan",
                    }
                    from services.scroll_composer import ScrollComposer
                    composer = ScrollComposer()
                    image = composer.compose(image, comp_map.get(composition, "vertical"))
                    log.append(f"🖼️ 装裱完成: {composition}")
                except Exception as e:
                    log.append(f"⚠️ 装裱失败: {e}")

            if use_aging:
                try:
                    from forgecore.post_process.aging_processor import AgingProcessor
                    aging = AgingProcessor()
                    tex = aging_texture if aging_texture != "none" else None
                    image = aging.apply(image.convert("RGB"), texture=tex, strength=float(aging_strength))
                    image = image.convert("RGBA")
                    log.append(f"📜 做旧完成 (纹理:{aging_texture}, 强度:{aging_strength})")
                except Exception as e:
                    log.append(f"⚠️ 做旧失败: {e}")

            clean_image = None
            if use_watermark:
                if save_clean_copy:
                    clean_image = image.copy()
                    log.append("🔒 已生成无水印留底副本")
                try:
                    from forgecore.post_process.watermark import WatermarkProcessor
                    wp = WatermarkProcessor()
                    image = wp.add_subtle_watermark(image.convert("RGB"), WATERMARK_TEXT, opacity=30)
                    image = image.convert("RGBA")
                    log.append(f"💧 水印完成 (文字: {WATERMARK_TEXT})")
                except Exception as e:
                    log.append(f"⚠️ 水印失败: {e}")

            return image, clean_image
        except Exception as e:
            log.append(f"❌ 后期处理整体失败: {e}")
            return image, None


def build_ui():
    app = ArtForgeApp()
    return app.build_ui()


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(inbrowser=True, share=False)