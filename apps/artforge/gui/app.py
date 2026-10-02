# apps/artforge/gui/app.py
import gradio as gr
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

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
                negative_input
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
    
    def _generate_image(self, engine_mode, api_provider, model_name, theme, preset, aspect, prompt, negative):
        """生成图片的核心逻辑"""
        try:
            start_time = datetime.now()
            width, height = self._parse_aspect_ratio(aspect)
            
            # ========== 分支 1：本地模型 ==========
            if engine_mode == "local":
                if not FORGE_CORE_AVAILABLE:
                    return None, "❌ ForgeCore 未安装，无法使用本地模型", ""
                return self._generate_with_local(model_name, prompt, negative, width, height, theme, preset)
            
            # ========== 分支 2：API 引擎 ==========
            elif engine_mode == "api":
                # 🔥 修复：补全 theme 和 preset 参数的传递
                return self._generate_with_api(api_provider, prompt, negative, width, height, theme, preset)
                
        except Exception as e:
            import traceback
            return None, f"❌ 生成失败: {str(e)}\n\n{traceback.format_exc()}", ""
            
        """生成图片的核心逻辑"""
        try:
            start_time = datetime.now()
            width, height = self._parse_aspect_ratio(aspect)
            
            # ========== 分支 1：本地模型 ==========
            if engine_mode == "local":
                if not FORGE_CORE_AVAILABLE:
                    return None, "❌ ForgeCore 未安装，无法使用本地模型"
                return self._generate_with_local(model_name, prompt, negative, width, height)
            
            # ========== 分支 2：API 引擎 ==========
            elif engine_mode == "api":
                return self._generate_with_api(api_provider, prompt, negative, width, height)
                
        except Exception as e:
            import traceback
            return None, f"❌ 生成失败: {str(e)}\n\n{traceback.format_exc()}"
    
    def _generate_image(self, engine_mode, api_provider, model_name, theme, preset, aspect, prompt, negative):
        """生成图片的核心逻辑"""
        try:
            start_time = datetime.now()
            width, height = self._parse_aspect_ratio(aspect)
            
            # ========== 分支 1：本地模型 ==========
            if engine_mode == "local":
                if not FORGE_CORE_AVAILABLE:
                    return None, "❌ ForgeCore 未安装，无法使用本地模型", ""
                return self._generate_with_local(model_name, prompt, negative, width, height, theme, preset)
            
            # ========== 分支 2：API 引擎 ==========
            elif engine_mode == "api":
                # 🔥 修复：补全 theme 和 preset 参数的传递
                return self._generate_with_api(api_provider, prompt, negative, width, height, theme, preset)
                
        except Exception as e:
            import traceback
            return None, f"❌ 生成失败: {str(e)}\n\n{traceback.format_exc()}", ""

    def _generate_with_api(self, provider, prompt, negative, width, height, theme=None, preset=None):
        """调用指定的 API 引擎"""
        log = f"✅ 使用 API 引擎: {provider}\n"
        log += f"提示词: {prompt}\n"
        log += f"尺寸: {width}x{height}\n"
        if theme:
            log += f"主题: {theme}\n"
        if preset:
            log += f"预设: {preset}\n"
        
        # 这里可以接入你原有的 api_engines.create_engine 逻辑
        if provider == "pollinations":
            log += "🚀 正在调用 Pollinations API (免费)..."
            # TODO: 调用 pollinations.generate(...)
        elif provider == "agnes":
            log += "🚀 正在调用 Agnes AI..."
            # TODO: 调用 agnes.generate(...)
        else:
            log += f"🚀 正在调用 {provider}..."
            
        return None, log + "\n(具体推理代码待接入)"
        
    def _generate_with_local(self, model_name, prompt, negative, width, height, theme, preset):
        """使用本地模型生成"""
        try:
            log = ["🚀 开始本地模型生成..."]
            log.append(f"📦 模型: {model_name}")
            log.append(f"📐 尺寸: {width}x{height}")
            log.append(f"🎨 主题: {theme} | 预设: {preset}")
            
            if not FORGE_CORE_AVAILABLE:
                return None, "\n".join(log) + "\n❌ ForgeCore 未就绪", ""

            # 1. 确定模型类型 (简单判断)
            model_type = "sd15" if "sd15" in model_name.lower() or "v1" in model_name.lower() else "sdxl"
            
            # 2. 获取模型绝对路径
            models = ModelRegistry.scan_checkpoints(model_type)
            model_path = None
            for m in models:
                if m["name"] == model_name:
                    model_path = m["absolute_path"]
                    break
            
            if not model_path:
                return None, "\n".join(log) + f"\n❌ 未找到模型文件: {model_name}", ""
            
            log.append(f"📂 绝对路径: {model_path}")
            
            # 3. 获取并加载本地引擎 (这里使用我们之前写好的 DiffusersEngine)
            from forgecore.engines.local_engine import LocalEngine
            
            log.append("⏳ 正在加载模型到内存 (首次加载可能需要 30-60 秒，请耐心等待)...")
            engine = LocalEngine(model_type=model_type, device="CPU")
            engine.load_model(model_path)
            
            # 4. 执行生成 (这里先返回模拟日志，后续你可以接入 engine.generate)
            log.append("✅ 模型加载完成！")
            log.append("🎨 正在执行推理... (此处为框架演示，真实推理代码待接入 engine.generate)")
            
            # 模拟生成结果路径
            result_path = str(Paths.OUTPUT_DIR / f"local_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            log.append(f"💾 预计保存至: {result_path}")
            
            final_prompt = f"[{theme}] {preset}, {prompt}"
            return None, "\n".join(log), final_prompt
            
        except Exception as e:
            import traceback
            return None, f"❌ 本地生成失败: {str(e)}\n\n{traceback.format_exc()}", ""


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