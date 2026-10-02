# apps/artforge/gui/app.py
import gradio as gr
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
# 在 import 区域添加这一行
from gui.common import load_env_config

# 导入 ForgeCore 配置和引擎
try:
    from forgecore.config.paths import Paths
    from forgecore.config.registry import ModelRegistry
    from forgecore.config.settings import settings
    from forgecore.engines.router import get_engine
    FORGE_CORE_AVAILABLE = True
except ImportError:
    FORGE_CORE_AVAILABLE = False
    print("⚠️ ForgeCore 模块未找到，将使用 API 模式")

class ArtForgeApp:
    def __init__(self):
        self.current_engine = None
        self.engine_type = "api"  # "api" or "local"
        
    def build_ui(self):
        """构建 Gradio 界面"""
        with gr.Blocks(title="ArtForge • 东方艺术生成工坊") as demo:
            gr.Markdown("""
            # 🎨 ArtForge • 东方艺术生成工坊
            """)
            
            with gr.Tabs():
                # ========== 生图标签页 ==========
                with gr.TabItem("🎨 生图"):
                    self._build_generation_tab()
                
                # ========== 其他标签页保持不变 ==========
                with gr.TabItem("🖼️ 鉴赏"):
                    gr.Markdown("鉴赏功能开发中...")
                    
                with gr.TabItem("📐 排版推送"):
                    gr.Markdown("排版推送功能开发中...")
                    
                with gr.TabItem("🔧 配置"):
                    self._build_config_tab()
            
        return demo
    
    def _build_generation_tab(self):
        """构建生图标签页"""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎨 生图参数")
                
                # ===== 引擎选择区域 (重构版) =====
                with gr.Group():
                    gr.Markdown("#### 🔌 引擎选择")
                    
                    # 1. 大模式切换：API vs 本地
                    engine_mode = gr.Radio(
                        choices=[
                            ("☁️ API 引擎 (云端)", "api"),
                            ("💻 本地模型 (OpenVINO/Diffusers)", "local")
                        ],
                        value="api",
                        label="生成模式",
                        info="选择使用云端 API 还是本地离线模型"
                    )
                    
                    # 2. API 提供商选择 (默认隐藏，选 API 时显示)
                    with gr.Group(visible=True) as api_config_group:
                        api_provider = gr.Dropdown(
                            choices=[
                                ("Pollinations (免费/推荐)", "pollinations"),
                                ("Free API (社区免费)", "freeapi"),
                                ("Agnes AI", "agnes"),
                                ("SiliconFlow (硅基流动)", "siliconflow"),
                                ("HuggingFace", "huggingface"),
                                ("Replicate", "replicate"),
                                ("Stability AI", "stability"),
                                ("通义万相 (Tongyi)", "tongyi"),
                                ("即梦 (Yige)", "yige"),
                                ("腾讯混元 (Hunyuan)", "hunyuan"),
                                ("OpenRouter", "openrouter"),
                            ],
                            value="pollinations",
                            label="选择 API 提供商",
                            info="部分引擎需要配置 API Key"
                        )
                        gr.Markdown("💡 *提示：Pollinations 和 FreeAPI 完全免费，无需配置 Key。*")

                    # 3. 本地模型配置 (默认隐藏，选本地时显示)
                    with gr.Group(visible=False) as local_config_group:
                        model_type_dropdown = gr.Dropdown(
                            choices=["SD1.5", "SDXL"],
                            value="SD1.5",
                            label="模型类型"
                        )
                        
                        model_dropdown = gr.Dropdown(
                            choices=self._get_local_models("sd15"),
                            label="选择模型",
                            info="从本地模型目录加载"
                        )
                        
                        # 刷新按钮
                        refresh_btn = gr.Button("🔄 刷新模型列表", size="sm")

                # ========== 事件绑定：引擎模式切换 ==========
                def on_engine_mode_change(mode):
                    """切换 API/本地 模式时，显示/隐藏对应配置区"""
                    if mode == "api":
                        return gr.update(visible=True), gr.update(visible=False)
                    else:
                        return gr.update(visible=False), gr.update(visible=True)
                
                engine_mode.change(
                    fn=on_engine_mode_change,
                    inputs=[engine_mode],
                    outputs=[api_config_group, local_config_group]
                )
                
                # 原有参数
                with gr.Group():
                    gr.Markdown("#### 📂 主题分类")
                    theme_dropdown = gr.Dropdown(
                        choices=["architecture", "landscape", "portrait", "fantasy", "anime"],
                        value="architecture",
                        label="主题分类"
                    )
                    
                    gr.Markdown("####  预设")
                    preset_dropdown = gr.Dropdown(
                        choices=["bridge", "pagoda", "garden", "mountain", "river"],
                        value="bridge",
                        label="预设场景"
                    )
                    
                    gr.Markdown("#### 🖼️ 画幅")
                    aspect_radio = gr.Radio(
                        choices=[
                            ("vertical (立轴 9:16)", "9:16"),
                            ("horizontal (横卷 16:9)", "16:9"),
                            ("byobu (屏风 4:3)", "4:3"),
                            ("fan (团扇 1:1)", "1:1"),
                        ],
                        value="9:16",
                        label="画幅比例"
                    )
                
                # 提示词
                with gr.Group():
                    gr.Markdown("#### ✍️ 提示词")
                    prompt_input = gr.Textbox(
                        label="正向提示词",
                        placeholder="输入描述，例如：一座古老的石桥，山水画风格...",
                        lines=3
                    )
                    
                    negative_input = gr.Textbox(
                        label="负向提示词",
                        placeholder="low quality, blurry, watermark",
                        lines=2
                    )

                # 5. ArtForge 特色：后期处理与装裱
                with gr.Accordion("️ ArtForge 特色后期与装裱", open=True):
                    # 装裱方式（核心功能）
                    composition_dd = gr.Dropdown(
                        choices=["无 (仅画心)", "立轴 (9:16)", "横卷 (16:9)", "屏风 (4:3)", "团扇 (1:1)", "册页 (2x2)"],
                        value="立轴 (9:16)",
                        label="装裱方式",
                        info="选择传统装裱格式，自动添加绫边、木轴等"
                    )
                    
                    use_aging_cb = gr.Checkbox(label="添加古画做旧效果 (宣纸纹理/泛黄)", value=True)
                    use_inscription_cb = gr.Checkbox(label="添加竖排题词与印章", value=True)
                    inscription_theme_dd = gr.Dropdown(
                        choices=["landscape", "portrait", "architecture", "yokai", "gufeng"],
                        value="gufeng",
                        label="题词主题"
                    ) 
                    
                # 生成按钮
                generate_btn = gr.Button("🎨 开始生成", variant="primary", size="lg")
            
            # 输出区域
            with gr.Column(scale=2):
                gr.Markdown("### 🖼️ 生成结果")
                output_image = gr.Image(label="生成的图片", type="filepath")
                output_info = gr.Textbox(label="生成信息", lines=5)
        
        # ========== 事件处理 ==========
        
        # 引擎切换逻辑
        def on_engine_change(engine_value):
            """引擎切换时的处理"""
            if engine_value == "local":
                if not FORGE_CORE_AVAILABLE:
                    return gr.update(visible=True), gr.update(visible=False), "⚠️ ForgeCore 未安装，无法使用本地模型"
                return gr.update(visible=True), gr.update(visible=True), "✅ 已切换到本地模型模式"
            else:
                return gr.update(visible=False), gr.update(visible=False), "✅ 已切换到 API 引擎模式"
        
        # ✅ 正确代码
        engine_mode.change(
           fn=on_engine_change,
           inputs=[engine_mode],
           outputs=[local_config_group, model_dropdown, output_info]
        )
        
        # 模型类型切换
        def on_model_type_change(model_type):
            """模型类型切换时更新模型列表"""
            model_type_key = "sd15" if model_type == "SD1.5" else "sdxl"
            models = self._get_local_models(model_type_key)
            return gr.update(choices=models, value=models[0] if models else None)
        
        model_type_dropdown.change(
            fn=on_model_type_change,
            inputs=[model_type_dropdown],
            outputs=[model_dropdown]
        )
        
        # 刷新模型列表
        def on_refresh_models(model_type):
            model_type_key = "sd15" if model_type == "SD1.5" else "sdxl"
            models = self._get_local_models(model_type_key, force_refresh=True)
            return gr.update(choices=models)
        
        refresh_btn.click(
            fn=on_refresh_models,
            inputs=[model_type_dropdown],
            outputs=[model_dropdown]
        )
        
        # 生成按钮
        generate_btn.click(
            fn=self._generate_image,
            inputs=[
                engine_mode,          # 新增：api 或 local
                api_provider,         # 新增：具体的 API 名称
                model_dropdown,       # 本地模型名
                theme_dropdown,
                preset_dropdown,
                aspect_radio,
                prompt_input,
                negative_input,
                composition_dd,  # 新增：装裱方式
                use_aging_cb,    # 做旧处理
                use_inscription_cb, 
                inscription_theme_dd
            ],
            outputs=[output_image, output_info]
        )
    
    def _get_local_models(self, model_type: str, force_refresh: bool = False) -> list:
        """获取本地模型列表"""
        if not FORGE_CORE_AVAILABLE:
            return ["ForgeCore 未安装"]
        
        try:
            models = ModelRegistry.scan_checkpoints(model_type)
            return [m["name"] for m in models]
        except Exception as e:
            print(f"⚠️ 获取模型列表失败: {e}")
            return ["获取模型列表失败"]
    
    def _generate_image(self, engine_mode, api_provider, model_name, theme, preset, aspect, prompt, negative, composition, use_aging, use_inscription, inscription_theme):
        """ArtForge 统一生成入口 (含装裱与后期)"""
        try:
            start_time = datetime.now()
            width, height = self._parse_aspect_ratio(aspect)
            
            #  核心修复：强制加入古画质感提示词，让 AI 直接在“旧纸”上作画
            full_prompt = prompt
            if theme: full_prompt = f"{theme}, {full_prompt}"
            if preset: full_prompt = f"{preset}, {full_prompt}"
            full_prompt += ", traditional Chinese painting, on aged xuan paper, ink wash texture, masterpiece, best quality"
            
            # ========== 分支 1：本地模型 ==========
            if engine_mode == "local":
                if not FORGE_CORE_AVAILABLE:
                    return None, "❌ ForgeCore 未安装，无法使用本地模型"
                return self._generate_with_local(model_name, full_prompt, negative, width, height, composition, use_aging, use_inscription, inscription_theme)
            
            # ========== 分支 2：API 引擎 ==========
            elif engine_mode == "api":
                return self._generate_with_api(api_provider, full_prompt, negative, width, height, composition, use_aging, use_inscription, inscription_theme)
                
        except Exception as e:
            import traceback
            return None, f"❌ 生成失败: {str(e)}\n\n{traceback.format_exc()}"

    def _generate_with_api(self, provider, prompt, negative, width, height, composition, use_aging, use_inscription, inscription_theme):
        """真实接入 ForgeCore API 引擎"""
        try:
            log = [f"🚀 正在调用 API 引擎: {provider}", f"📐 尺寸: {width}x{height}"]
            
            from forgecore.engines import create_engine
            from gui.common import load_env_config
            
            config = load_env_config()
            log.append("⏳ 正在初始化引擎并发送请求...")
            engine = create_engine(provider, config)
            
            log.append(f"📝 提示词: {prompt[:50]}...")
            image = engine.generate_single(
                prompt=prompt, negative=negative, width=width, height=height,
                steps=25, cfg=7.5, seed=None
            )
            
            log.append("✅ API 返回成功，正在处理结果...")
            
            # 🔥 核心：在保存前应用后期处理 (包含装裱)
            image = self._apply_post_process(image, composition, use_aging, use_inscription, inscription_theme, log)
            
            return self._save_engine_output(image, f"api_{provider}", log)
        except ImportError as e:
            return None, f" 导入失败: {e}"
        except Exception as e:
            import traceback
            return None, f"❌ API 生成失败: {str(e)}\n\n{traceback.format_exc()}"

    def _generate_with_local(self, model_name, prompt, negative, width, height, composition, use_aging, use_inscription, inscription_theme):
        """真实接入本地 Diffusers 引擎"""
        try:
            log = [f"💻 正在使用本地模型: {model_name}", f"📐 尺寸: {width}x{height}"]
            if not FORGE_CORE_AVAILABLE:
                return None, "❌ ForgeCore 未就绪"

            model_type = "sd15" if "sd15" in model_name.lower() or "v1" in model_name.lower() else "sdxl"
            models = ModelRegistry.scan_checkpoints(model_type)
            model_path = next((m["absolute_path"] for m in models if m["name"] == model_name), None)
            
            if not model_path:
                return None, f"❌ 找不到模型文件: {model_name}"
            
            log.append(f" 绝对路径: {model_path}")
            
            from forgecore.engines.local_engine import DiffusersEngine
            log.append("⏳ 正在加载模型到内存...")
            engine = DiffusersEngine(model_type=model_type, device="CPU")
            engine.load_model(model_path)
            
            log.append(" 正在执行本地推理...")
            image = engine.generate(prompt=prompt, negative_prompt=negative, width=width, height=height)
            
            log.append("✅ 本地推理完成！")
            
            # 🔥 核心：在保存前应用后期处理 (包含装裱)
            image = self._apply_post_process(image, composition, use_aging, use_inscription, inscription_theme, log)
            
            return self._save_engine_output(image, "local", log)
        except Exception as e:
            import traceback
            return None, f"❌ 本地生成失败: {str(e)}\n\n{traceback.format_exc()}"
            
    # ============================================================
    # 🔥 新增：通用的引擎结果处理与保存辅助方法
    # ============================================================

    def _apply_post_process(self, image, composition, use_aging, use_inscription, inscription_theme, log_list):
        """ArtForge 标准后期流水线：题词 -> 装裱 -> 边缘做旧"""
        if image is None:
            return None
            
        try:
            from PIL import Image
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
                
            width, height = image.size
            
            # 1. 题词与印章 (在画心上完成)
            if use_inscription:
                try:
                    from forgecore.post_process.inscription_generator import InscriptionGenerator
                    # 修复导入路径
                    import sys
                    from pathlib import Path
                    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
                    from compose_artwork import InscriptionRenderer
                    from forgecore.post_process.seal_generator import SealGenerator
                    
                    log_list.append("✍️ 正在生成题词...")
                    ig = InscriptionGenerator()
                    inscription_text = "山水有清音" 
                    try:
                        text, _ = ig.generate(theme=inscription_theme, format="auto", return_meta=True)
                        if text: inscription_text = text
                    except: pass
                    
                    font_size = max(24, int(min(width, height) * 0.045))
                    renderer = InscriptionRenderer()
                    image = renderer.render(
                        image, inscription_text, font_size=font_size,
                        color=(45, 40, 35), position="top_right",
                        margin=int(min(width, height) * 0.055),
                        max_chars_per_col=8
                    )
                    log_list.append(f"✅ 题词完成: {inscription_text}")
                    
                    log_list.append("🔴 正在添加印章...")
                    sg = SealGenerator()
                    image = sg.apply_scheme(image, "東方藝術", scheme="default", margin_ratio=0.05)
                    log_list.append("✅ 印章完成")
                except Exception as e:
                    log_list.append(f"⚠️ 题词/印章失败 (跳过): {e}")

            # 2. 装裱 (核心功能：将画心放入立轴/横卷等)
            if composition and composition != "无 (仅画心)":
                try:
                    # 导入装裱器
                    import sys
                    from pathlib import Path
                    # 确保能导入 apps/artforge/services
                    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
                    from services.scroll_composer import ScrollComposer
                    
                    log_list.append(f"🖼️ 正在进行 {composition} 装裱...")
                    composer = ScrollComposer()
                    
                    # 映射 UI 选项到 ScrollComposer 的 composition 参数
                    comp_map = {
                        "立轴 (9:16)": "vertical",
                        "横卷 (16:9)": "horizontal",
                        "屏风 (4:3)": "byobu",
                        "团扇 (1:1)": "fan",
                        "册页 (2x2)": "album"
                    }
                    comp_type = comp_map.get(composition, "vertical")
                    
                    # 调用装裱方法
                    image = composer.compose(image, comp_type)
                    log_list.append(f"✅ 装裱完成 ({composition})")
                except Exception as e:
                    log_list.append(f"⚠️ 装裱失败 (跳过): {e}")
                    import traceback
                    log_list.append(f"   错误详情: {str(e)}")

            # 3. 边缘做旧 (仅对装裱后的整体进行轻微泛黄/磨损)
            if use_aging:
                try:
                    from forgecore.post_process.aging_processor import AgingProcessor
                    log_list.append(" 正在应用边缘做旧效果...")
                    aging = AgingProcessor()
                    # 降低强度，仅做边缘处理
                    image = aging.apply(image.convert("RGB"), texture="xuan_paper", strength=0.3)
                    image = image.convert("RGBA")
                    log_list.append("✅ 边缘做旧完成")
                except Exception as e:
                    log_list.append(f"⚠️ 做旧失败 (跳过): {e}")

            return image
        except Exception as e:
            log_list.append(f"❌ 后期处理整体失败: {e}")
            return image
            
    def _save_engine_output(self, result, prefix, log_list):
        """
        兼容处理不同引擎的返回结果 (PIL Image, URL 字符串, 或 Dict)
        """
        if result is None:
            return None, "\n".join(log_list) + "\n⚠️ 引擎返回为空，请检查 API Key 或模型配置。", ""
            
        final_image = None
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = Paths.OUTPUT_DIR / f"{prefix}_{timestamp}.png"
        
        try:
            # 情况 1: 返回的是 PIL Image 对象
            if hasattr(result, 'save'):
                final_image = result
                
            # 情况 2: 返回的是 URL 字符串 (如 Pollinations 直接返回图片链接)
            elif isinstance(result, str) and result.startswith('http'):
                import requests
                log_list.append(f" 正在下载图片: {result[:50]}...")
                response = requests.get(result, timeout=60)
                response.raise_for_status()
                from PIL import Image
                import io
                final_image = Image.open(io.BytesIO(response.content))
                
            # 情况 3: 返回的是字典 (如 {'image': ..., 'url': ...})
            elif isinstance(result, dict):
                if 'image' in result and hasattr(result['image'], 'save'):
                    final_image = result['image']
                elif 'url' in result and result['url'].startswith('http'):
                    # 递归调用处理 URL
                    return self._save_engine_output(result['url'], prefix, log_list)
                    
            # 保存文件
            if final_image:
                Paths.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                final_image.save(save_path)
                log_list.append(f"💾 图片已保存: {save_path}")
                return str(save_path), "\n".join(log_list), ""
            else:
                return None, "\n".join(log_list) + "\n️ 无法识别引擎返回的数据格式。", ""
                
        except Exception as e:
            return None, "\n".join(log_list) + f"\n❌ 保存图片时出错: {str(e)}", ""


    def _parse_aspect_ratio(self, aspect: str) -> tuple:
        """解析画幅比例"""
        ratios = {
            "9:16": (576, 1024),
            "16:9": (1024, 576),
            "4:3": (768, 576),
            "1:1": (768, 768),
        }
        return ratios.get(aspect, (512, 512))
    
    def _build_config_tab(self):
        """构建配置标签页"""
        with gr.Group():
            gr.Markdown("###  路径配置")
            
            if FORGE_CORE_AVAILABLE:
                gr.Markdown(f"""
                **模型基目录**: {Paths.BASE_MODELS_DIR}
                
                **SD1.5 目录**: {Paths.SD15_DIR}
                
                **SDXL 目录**: {Paths.SDXL_DIR}
                
                **输出目录**: {Paths.OUTPUT_DIR}
                """)
                
                # 显示当前可用的模型
                sd15_models = ModelRegistry.scan_checkpoints("sd15")
                sdxl_models = ModelRegistry.scan_checkpoints("sdxl")
                
                gr.Markdown(f"""
                ### 📦 已检测到的模型
                
                **SD1.5**: {len(sd15_models)} 个
                
                **SDXL**: {len(sdxl_models)} 个
                """)
            else:
                gr.Markdown("⚠️ ForgeCore 未安装，无法显示配置")

def build_ui():
    """入口函数"""
    app = ArtForgeApp()
    return app.build_ui()

if __name__ == "__main__":
    demo = build_ui()
    demo.launch(inbrowser=True, share=False, theme=gr.themes.Soft())