"""ArtForge GUI 主入口 (全功能完整重构版 - 修复返回值数量问题)"""
import gradio as gr
import os
import sys
import random
import tempfile
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from PIL import Image

# ============================================================
# 1. 路径注入与依赖导入
# ============================================================
APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# 🔥 已切换为共享东方美学库
PRESETS_DIR = PROJECT_ROOT / "shared_assets" / "presets_by_app" / "oriental_forge"

if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_ROOT) not in sys.path: sys.path.insert(0, str(APP_ROOT))

try:
    from forgecore.config.paths import Paths
    from forgecore.config.registry import ModelRegistry
    from forgecore.engines import create_engine          # 🆕 补上这个
    from forgecore.skills.manager import skill_manager   # 🆕 补上这个    
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
        self.presets_map: Dict[str, List[Dict]] = {}
        self.categories: List[str] = []
        self.loras: List[Dict] = []
        
        # ✅ 新增：定义预设库根目录和当前选中的库
        self.PRESETS_BASE = PROJECT_ROOT / "shared_assets" / "presets_by_app"
        self.current_lib = "oriental_forge" # 默认库，你可以改成 "anime_forge"
        
        # 初始加载默认库
        self._load_presets(self.current_lib)
        self._load_loras()

    def _load_presets(self, lib_name: str):
        """动态扫描指定预设库目录 (兼容新格式)"""
        self.current_lib = lib_name
        target_dir = self.PRESETS_BASE / lib_name
        print(f"🔍 正在扫描预设库: {lib_name} -> {target_dir}")
        
        # 清空旧数据
        self.presets_map = {}
        self.categories = []
        
        if not target_dir.exists():
            print(f" 预设库目录不存在: {target_dir}")
            return
            
        # 扫描逻辑：遍历子文件夹作为分类
        for theme_dir in sorted(target_dir.iterdir()):
            if not theme_dir.is_dir() or theme_dir.name.startswith('_'):
                continue
            cat_name = theme_dir.name
            self.categories.append(cat_name)
            self.presets_map[cat_name] = []
            
            # 遍历 .py 预设文件
            for py_file in sorted(theme_dir.glob("*.py")):
                if py_file.name.startswith('_') or py_file.name == '__init__.py':
                    continue
                try:
                    spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "PRESET"):
                        preset_data = mod.PRESET
                        preset_data["file_path"] = str(py_file) # 保存路径供后续使用
                        self.presets_map[cat_name].append(preset_data)
                except Exception as e:
                    print(f"⚠️ 加载预设失败 {py_file.name}: {e}")
                    
        print(f"✅ 库 [{lib_name}] 加载完成: {len(self.categories)} 个分类")

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

    def _get_models(self, model_type: str) -> list:
        if not FORGE_CORE_AVAILABLE: return ["ForgeCore 未就绪"]
        try: return [m["name"] for m in ModelRegistry.scan_checkpoints(model_type)]
        except: return ["扫描失败"]

    def _save_image_automatically(self, image: Image.Image, prefix: str = "artforge") -> str:
        """自动保存图片到 output 目录"""
        if image is None:
            return ""
        try:
            save_dir = Paths.OUTPUT_DIR if FORGE_CORE_AVAILABLE else APP_ROOT / "output"
            save_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = save_dir / f"{prefix}_{timestamp}.png"
            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGB')
            image.save(save_path)
            return str(save_path)
        except Exception as e:
            print(f"⚠️ 自动保存图片失败: {e}")
            return ""

    def build_ui(self):
        """构建 Gradio 界面 (5个Tab)"""
        with gr.Blocks(title="ArtForge · 东方艺术生成工坊", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🎎 ArtForge · 东方艺术生成工坊")
            with gr.Tabs():
                with gr.Tab("🎨 生图"):
                    self._build_generation_tab()
                with gr.Tab("🖼️ 图生图"):                    
                    self._build_img2img_tab()
                with gr.Tab("🪄 像素魔法"):
                    self._build_pixel_magic_tab()
                with gr.Tab("️ 鉴赏与排版"):
                    gr.Markdown("### 图片鉴赏与排版推送\n(功能开发中... 将接入 BLIP/LLM 进行自动鉴赏与微信排版)")
                with gr.Tab("⚙️ 配置"):
                    self._build_config_tab()
        return demo

    def _build_generation_tab(self):
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Group():
                    gr.Markdown("###  主题与预设")
                    # ✅ 新增：预设库选择 Dropdown
                    # 扫描 PRESETS_BASE 下所有文件夹作为选项
                    available_libs = [d.name for d in self.PRESETS_BASE.iterdir() 
                                      if d.is_dir() and not d.name.startswith('_')]
                    preset_library_dd = gr.Dropdown(
                        choices=available_libs,
                        value=self.current_lib,
                        label=" 预设库 (Preset Library)"
                    )
                    # 原有的分类 Dropdown
                    category_dd = gr.Dropdown(
                        choices=self.categories,
                        value=(self.categories[0] if self.categories else None),
                        label="主题分类 (Category)"
                    )
                    # 原有的预设 Dropdown
                    first_cat_presets = self.presets_map.get(self.categories[0], []) if self.categories else []
                    preset_dd = gr.Dropdown(
                        choices=[p["name"] for p in first_cat_presets],
                        value=(first_cat_presets[0]["name"] if first_cat_presets else None),
                        label="预设场景 (Preset)"
                    )
                    prompt_input = gr.Textbox(label="正向提示词 (Prompt)", lines=4, placeholder="由预设自动生成...")
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
                        refresh_model_btn = gr.Button(" 刷新模型", size="sm")
                
                # 3. LoRA 设置 (仅本地模型有效)
                with gr.Group(visible=False) as lora_group:
                    gr.Markdown("###  LoRA 扩展")
                    lora_dd = gr.Dropdown(
                        choices=[l["name"] for l in self.loras],
                        label="选择 LoRA", allow_custom_value=True
                    )
                    lora_weight = gr.Slider(minimum=0.0, maximum=1.5, value=0.7, step=0.1, label="LoRA 权重")
                
                # 4. 高级参数
                with gr.Group():
                    gr.Markdown("### ⚙️ 高级参数")
                    with gr.Row():
                        steps_slider = gr.Slider(minimum=10, maximum=50, value=15, step=1, label="采样步数 (Steps)")
                        cfg_slider = gr.Slider(minimum=1.0, maximum=15.0, value=7.5, step=0.5, label="CFG Scale")
                    with gr.Row():
                        seed_input = gr.Number(value=-1, label="种子 (Seed, -1 为随机)", precision=0)
                        count_slider = gr.Slider(minimum=1, maximum=4, value=1, step=1, label="生成数量 (Batch Size)")
                
                # 5. 后期处理与装裱 (逻辑优化版)
                with gr.Group():
                    gr.Markdown("### ️ 后期处理与装裱")
                    
                    # 1. 装裱方式 (全局基础，独立一行)
                    composition_dd = gr.Dropdown(
                        choices=["无 (仅画心)", "立轴 (9:16)", "横卷 (16:9)", "屏风 (4:3)", "团扇 (1:1)"],
                        value="立轴 (9:16)", label="装裱方式"
                    )

                    # 2. 核心功能开关 (最常用的三个，直接露出来)
                    with gr.Row():
                        use_aging_cb = gr.Checkbox(label="启用古画做旧", value=False, scale=1)
                        use_inscription_cb = gr.Checkbox(label="启用竖排题词", value=True, scale=1)
                        use_seal_cb = gr.Checkbox(label="启用印章", value=True, scale=1)

                    # 3. 做旧高级设置 (折叠，内部左右对齐)
                    with gr.Accordion("📜 做旧高级设置", open=False):
                        with gr.Row():
                            aging_strength = gr.Slider(
                                minimum=0.1, maximum=1.0, value=0.5, step=0.1, 
                                label="做旧强度 (0.1=轻微泛黄, 1.0=重度破损)",
                                scale=2
                            )
                            aging_texture = gr.Dropdown(
                                choices=["xuan_paper", "silk", "aged", "brown", "none"], 
                                value="xuan_paper", 
                                label="纸张纹理类型 (none=无纹理)",
                                scale=1
                            )

                    # 4. 题词高级设置 (折叠，把“内置库”移回这里，逻辑归位！)
                    with gr.Accordion("🖌️ 题词高级设置", open=False):
                        with gr.Row():
                            inscription_language_dd = gr.Dropdown(
                                choices=["auto", "zh (中文)", "ja (日文)", "en (英文)"],
                                value="auto", label="题词语言", scale=1
                            )
                            inscription_format_dd = gr.Dropdown(
                                choices=[
                                    ("自动 (Auto)", "auto"), 
                                    ("五言绝句 (20字)", "wuyan"), 
                                    ("七言绝句 (28字)", "qiyan"), 
                                    ("和歌 (Waka)", "waka"), 
                                    ("俳句 (Haiku)", "haiku"), 
                                    ("题跋 (散文)", "tiba")
                                ],
                                value="auto", 
                                label="题词体裁 (Format)", scale=1
                            )
                            inscription_position_dd = gr.Dropdown(
                                choices=[
                                    ("右上题诗 (Top Right)", "top_right"), 
                                    ("左下落款 (Bottom Left)", "bottom_left"), 
                                    ("左上角 (Top Left)", "top_left")
                                ],
                                value="top_right", 
                                label="题词位置 (Position)", scale=1
                            )
                        
                        # 👇 移回题词区域，逻辑就通了 👇
                        with gr.Row():
                            use_library_only_cb = gr.Checkbox(
                                label="仅用内置诗句库 (离线/秒出，不调用 AI)", value=False
                            )

                    # 5. 其他/实验性功能 (剩下的低频选项)
                    with gr.Row():
                        use_watermark_cb = gr.Checkbox(label="隐形水印", value=False, scale=1)
                        # 👇 新增：同时保存无水印原图 👇
                        save_clean_copy_cb = gr.Checkbox(label="同时保存无水印留底版 (自己收藏)", value=False)
                        # 👆 新增结束 👆

                        use_appraise_cb = gr.Checkbox(label="AI 自动鉴赏 (BLIP)", value=False, scale=1)
                        
                # 生成按钮 (保留原位)
                generate_btn = gr.Button("🎨 开始生成", variant="primary", size="lg")
            
            # 右侧输出列 (保留原位，绝对不丢)
            with gr.Column(scale=2):
                output_image = gr.Image(label="生成结果", type="filepath", height=700)
                output_info = gr.Textbox(label="执行日志", lines=12)

        # ========== 事件绑定 ==========
        # 1. 切换预设库 -> 更新分类和预设列表
        def on_lib_change(lib_name):
            self._load_presets(lib_name) # 重新加载数据
            # 准备返回的新选项
            new_cats = self.categories
            first_cat = new_cats[0] if new_cats else None
            new_presets = self.presets_map.get(first_cat, []) if first_cat else []
            first_preset_name = new_presets[0]["name"] if new_presets else None
            # 返回更新后的 category_dd 和 preset_dd
            return gr.update(choices=new_cats, value=first_cat), gr.update(choices=[p["name"] for p in new_presets], value=first_preset_name)
        
        preset_library_dd.change(
            fn=on_lib_change,
            inputs=[preset_library_dd],
            outputs=[category_dd, preset_dd]
        )
        
        # 2. 切换分类 -> 更新预设列表 (保留原有逻辑)
        def on_category_change(cat):
            lst = self.presets_map.get(cat, [])
            names = [p["name"] for p in lst]
            return gr.update(choices=names, value=(names[0] if names else None))
        
        category_dd.change(fn=on_category_change, inputs=category_dd, outputs=preset_dd)
        
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
                use_aging_cb, aging_strength, aging_texture, 
                use_inscription_cb, inscription_format_dd, inscription_position_dd, 
                use_library_only_cb,
                use_seal_cb, use_watermark_cb,save_clean_copy_cb, 
                inscription_language_dd, use_appraise_cb
            ],
            outputs=[output_image, output_info]  # 🔥 严格对应 2 个输出
        )

    def _build_img2img_tab(self):
        """构建图生图 & ControlNet Tab (集成到 app.py)"""
        with gr.Tab("🖼️ 图生图 & ControlNet"):
            gr.Markdown("### 🖼️ 图生图 / ControlNet 工作台")
            gr.Markdown("💡 **核心逻辑**：上传参考图锁定特征，通过提示词引导继续创作。默认使用 Agnes API 图生图，也支持本地 ControlNet 模型。")
            
            with gr.Row():
                with gr.Column(scale=1):
                    # 1. 核心：参考图上传
                    self.i2i_ref_image = gr.Image(label="📎 上传参考图 (Control Source / 图生图底图)", type="pil", height=300)
                    
                    # 2. 引擎选择
                    self.i2i_engine_mode = gr.Radio(
                        choices=[("☁️ Agnes API (图生图)", "agnes"), ("💻 本地模型 (ControlNet)", "local")],
                        value="agnes", 
                        label="生成引擎"
                    )
                    
                    # 本地模型选择 (复用 app.py 已有的模型扫描逻辑，如果有的话；这里新建一个确保可用)
                    from forgecore.config.registry import ModelRegistry
                    local_models = [m["name"] for m in ModelRegistry.scan_checkpoints("sd15")]
                    self.i2i_local_model = gr.Dropdown(
                        choices=local_models,
                        label="本地模型 (SD1.5) - 仅本地引擎生效",
                        value=local_models[0] if local_models else None
                    )

                    # 3. 提示词
                    self.i2i_prompt = gr.Textbox(label="提示词 (Prompt - 描述你想要的变化)", value="masterpiece, best quality, detailed face", lines=2)
                    self.i2i_neg = gr.Textbox(label="负面提示词 (仅本地模型生效)", value="worst quality, lowres, bad anatomy", lines=1)
                    
                    # 4. 控制参数
                    with gr.Group():
                        gr.Markdown("#### 🎛️ 控制参数")
                        self.i2i_cn_type = gr.Dropdown(
                            choices=["openpose", "canny", "depth", "lineart", "hed", "无 (纯图生图)"],
                            label="ControlNet 类型 / 参考方式", value="无 (纯图生图)"
                        )
                        self.i2i_strength = gr.Slider(0.1, 1.0, value=0.6, label="重绘幅度 / ControlNet 强度 (0.1=微调, 1.0=大改)")
                        
                    self.i2i_btn = gr.Button("🚀 开始图生图", variant="primary", size="lg")
                    
                with gr.Column(scale=1):
                    self.i2i_out = gr.Image(label="生成结果", type="pil", height=400)
                    self.i2i_log = gr.Textbox(label="生成日志", lines=10)

        # 绑定事件
        self.i2i_btn.click(
            fn=self._run_img2img,
            inputs=[self.i2i_ref_image, self.i2i_engine_mode, self.i2i_local_model, self.i2i_prompt, self.i2i_neg, self.i2i_cn_type, self.i2i_strength],
            outputs=[self.i2i_out, self.i2i_log]
        )

    def _run_img2img(self, ref_img, mode, model_name, prompt, negative, cn_type, strength):
        """执行图生图逻辑 (包含自动保存)"""
        logs = ["🚀 启动图生图 / ControlNet 流水线..."]
        
        if ref_img is None:
            return None, "❌ 必须上传参考图！图生图/ControlNet 需要底图来锁定特征。"

        try:
            final_image = None
            
            # ==========================================
            # 路径 A: Agnes API 图生图 (默认)
            # ==========================================
            if mode == "agnes":
                logs.append(f"☁️ 使用 Agnes API 图生图")
                from forgecore.engines import create_engine
                from gui.common import load_env_config
                
                config = load_env_config()
                engine = create_engine("agnes", config)
                
                # ✅ 修复：Agnes 的 image_to_image 不需要 negative 参数
                try:
                    if hasattr(engine, 'image_to_image'):
                        logs.append(" 调用 engine.image_to_image...")
                        final_image = engine.image_to_image(
                            prompt=prompt, 
                            image=ref_img,
                            strength=strength,
                            width=768, height=1024
                        )
                    else:
                        logs.append("⚠️ 引擎无 image_to_image，降级为文生图")
                        final_image = engine.generate_single(prompt=prompt, width=768, height=1024)
                except TypeError:
                    # 兼容签名差异
                    final_image = engine.image_to_image(prompt=prompt, images=[ref_img], strength=strength)
                    
                logs.append("✅ Agnes API 图生图完成")

            # ==========================================
            # 路径 B: 本地模型 ControlNet
            # ==========================================
            else:
                if not model_name:
                    return None, "❌ 选择本地引擎时，必须选择本地模型。"
                
                from forgecore.config.registry import ModelRegistry
                from forgecore.skills.manager import skill_manager
                
                all_models = ModelRegistry.scan_checkpoints("sd15")
                model_obj = next((m for m in all_models if m["name"] == model_name), None)
                if not model_obj:
                    return None, "❌ 找不到模型路径"
                model_path = model_obj["absolute_path"]
                logs.append(f"📂 本地模型: {model_name}")

                # 调用 ControlNet Skill
                if cn_type and cn_type != "无 (纯图生图)":
                    logs.append(f"🎛️ 调用本地 ControlNet (类型: {cn_type})")
                    res = skill_manager.run(
                        "controlnet", action="generate", image=ref_img, prompt=prompt,
                        negative_prompt=negative, model_path=model_path,
                        controlnet_type=cn_type, controlnet_conditioning_scale=strength
                    )
                else:
                    logs.append(f"🖼️ 调用本地图生图")
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
            # 核心：自动保存功能 (参考 app.py 原有逻辑)
            # ==========================================
            if final_image is not None:
                from forgecore.config.paths import Paths
                from datetime import datetime
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                # 使用 Paths.OUTPUT_DIR，如果不可用则回退到 output 目录
                save_dir = Paths.OUTPUT_DIR if hasattr(Paths, 'OUTPUT_DIR') else Path("output")
                save_dir.mkdir(parents=True, exist_ok=True)
                
                save_path = save_dir / f"img2img_{timestamp}.png"
                final_image.save(save_path)
                logs.append(f"💾 图片已自动保存: {save_path}")
                
                return final_image, "\n".join(logs)
            else:
                return None, "\n".join(logs) + "\n❌ 未生成有效图片"

        except Exception as e:
            import traceback
            return None, f"❌ 执行出错: {str(e)}\n{traceback.format_exc()}"

    # ============================================================
    # 🆕 Tab 3: 像素魔法 (Pixel Magic)
    # ============================================================
    def _build_pixel_magic_tab(self):
        """构建像素魔法 Tab (一键像素编辑)"""
        import tempfile
        from forgecore.skills.manager import skill_manager
        
        PIXEL_SKILLS = [
            "add_glasses", "add_tattoo", "add_animal_ears", "add_background_objects",
            "change_hair", "change_age", "change_gender", "change_body_type", "change_expression",
            "change_eye_color", "change_makeup", "change_skin_tone", "change_nationality", "change_face",
            "change_clothes", "change_clothing_style", "remove_clothes",
            "change_pose", "change_perspective", "expand_to_full_body",
            "change_background", "change_furniture", "change_lighting", "day_night_transfer", "season_transfer", "weather_transfer",
            "remove_object", "replace_object",
            "anime_to_real", "real_to_anime", "style_transfer", "sketch_to_real", "colorize_sketch", "photo_realistic",
            "fix_human_anatomy", "mosaic_reducer", "old_photo_restore", "photo_restorer", "human_to_robot", "fantasy_character", "mecha_generator",
            "intimate_closeup", "bathroom_nude", "beach_lingerie", "bedroom_lingerie", "bedroom_nude", "pool_nude", "studio_nude", "nude_oil_painting", "nude_sculpture",
        ]
        
        with gr.Row():
            with gr.Column(scale=1):
                magic_skill_dd = gr.Dropdown(choices=PIXEL_SKILLS, value="add_glasses", label="✨ 选择魔法技能")
                magic_ref_image = gr.Image(label="📎 上传参考图 (必须)", type="pil", height=300)
                magic_engine_mode = gr.Radio(choices=[("☁️ Agnes API (模拟)", "agnes"), ("💻 本地模型 (推荐)", "local")], value="local", label="生成引擎")
                local_models = [m["name"] for m in ModelRegistry.scan_checkpoints("sd15")] if FORGE_CORE_AVAILABLE else []
                magic_local_model = gr.Dropdown(choices=local_models, label="本地模型", value=local_models[0] if local_models else None)
                magic_btn = gr.Button("✨ 施展魔法", variant="primary", size="lg")
            with gr.Column(scale=1):
                magic_out = gr.Image(label="✨ 结果", type="pil", height=400)
                magic_log = gr.Textbox(label="日志", lines=10)

        def run_pixel_magic(skill_name, ref_img, mode, model_name):
            logs = [f"✨ 启动: {skill_name}"]
            if ref_img is None: return None, "❌ 必须上传参考图！"
            try:
                final_image = None
                if mode == "agnes":
                    logs.append(f"☁️ 使用 Agnes API 模拟 {skill_name}...")
                    prompt_map = {
                        "add_glasses": "wearing elegant glasses, sophisticated, masterpiece",
                        "add_tattoo": "with beautiful tattoo on skin, artistic, masterpiece",
                        "change_hair": "different hairstyle, detailed hair, masterpiece",
                        "change_background": "beautiful new background, scenic, masterpiece",
                        "remove_object": "clean background, no objects, masterpiece",
                    }
                    sim_prompt = prompt_map.get(skill_name, f"{skill_name.replace('_', ' ')}, masterpiece")
                    from gui.common import load_env_config
                    engine = create_engine("agnes", load_env_config())
                    try:
                        final_image = engine.image_to_image(prompt=sim_prompt, image=ref_img, strength=0.6, width=768, height=1024)
                    except TypeError:
                        final_image = engine.image_to_image(prompt=sim_prompt, images=[ref_img], strength=0.6)
                    logs.append("✅ Agnes API 模拟执行成功")
                else:
                    if not model_name: return None, "❌ 请选择本地模型"
                    model_obj = next((m for m in ModelRegistry.scan_checkpoints("sd15") if m["name"] == model_name), None)
                    if not model_obj: return None, "❌ 找不到模型"
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        ref_img.save(tmp.name)
                        temp_img_path = tmp.name
                    logs.append(f"📂 图片暂存: {Path(temp_img_path).name}")
                    output_path = temp_img_path.replace(".png", f"_{skill_name}_out.png")
                    kwargs = {"image_path": temp_img_path, "output_path": output_path, "model_path": model_obj["absolute_path"]}
                    logs.append(f"📂 模型: {model_name}")
                    res = skill_manager.run(skill_name, **kwargs)
                    success = False
                    if res.get("status") == "success":
                        res_data = res.get("result", {})
                        out_p = res_data.get("output_path") or res_data.get("image_path")
                        if out_p and Path(out_p).exists():
                            final_image = Image.open(out_p)
                            success = True
                        elif "image" in res_data and isinstance(res_data["image"], Image.Image):
                            final_image = res_data["image"]
                            success = True
                        logs.append("✅ 本地技能执行成功")
                    else:
                        logs.append(f"❌ 本地技能失败: {res.get('error')}")
                        if "unexpected keyword argument" in res.get("error", ""):
                            logs.append("🔄 降级重试...")
                            kwargs.pop("output_path", None)
                            res = skill_manager.run(skill_name, **kwargs)
                            if res.get("status") == "success":
                                res_data = res.get("result", {})
                                out_p = res_data.get("output_path") or res_data.get("image_path")
                                if out_p and Path(out_p).exists():
                                    final_image = Image.open(out_p)
                                    success = True
                                    logs.append("✅ 降级成功")
                    try: os.remove(temp_img_path)
                    except: pass
                if final_image:
                    save_path = self._save_image_automatically(final_image, prefix=f"magic_{skill_name}")
                    if save_path: logs.append(f"💾 已保存: {save_path}")
                    return final_image, "\n".join(logs)
                return None, "\n".join(logs) + "\n❌ 未能生成图片"
            except Exception as e:
                return None, f"❌ 错误: {e}"

        magic_btn.click(fn=run_pixel_magic, inputs=[magic_skill_dd, magic_ref_image, magic_engine_mode, magic_local_model], outputs=[magic_out, magic_log])

    def _generate_image(self, engine_mode, api_provider, model_name, category, preset_name, composition, 
                        prompt, negative, lora_name, lora_weight, steps, cfg, seed, count,
                        use_aging,aging_strength, aging_texture,
                        use_inscription, inscription_format, inscription_position, 
                        use_library_only,
                        use_seal, use_watermark, save_clean_copy,inscription_lang, use_appraise):
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
            
            # 3. 后期处理流水线 (参数严格对齐)
            if ARTFORGE_CORE_AVAILABLE:
                final_image, clean_image = self._apply_post_process(
                    final_image, composition,
                    use_aging, aging_strength, aging_texture,
                    use_inscription, inscription_lang, inscription_format, inscription_position, use_library_only,
                    use_seal, use_watermark, save_clean_copy,
                    category, log
                )
            else:
                clean_image = None                
                
            # 4. 保存 (双轨保存)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_dir = Paths.OUTPUT_DIR if FORGE_CORE_AVAILABLE else APP_ROOT / "output"
            save_dir.mkdir(parents=True, exist_ok=True)
            #save_path = save_dir / f"artforge_{timestamp}.png"

            # A. 保存主图 (带水印/完整后期)
            if final_image:
                main_path = save_dir / f"artforge_{timestamp}.png"
                final_image.save(main_path)
                log.append(f"💾 分享版已保存: {main_path}")
            
            # B. 保存留底图 (无水印)
            if clean_image is not None:
                clean_path = save_dir / f"artforge_{timestamp}_clean.png" # 加 _clean 后缀
                clean_image.save(clean_path)
                log.append(f" 留底版已保存: {clean_path}")
            
            return str(save_path), "\n".join(log)  # 🔥 严格返回 2 个值
            
        except Exception as e:
            import traceback
            return None, f"❌ 生成崩溃: {str(e)}\n\n{traceback.format_exc()}"  # 🔥 严格返回 2 个值

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

    def _apply_post_process_old(self, image, composition,
                            use_aging, aging_strength, aging_texture,
                            use_inscription, inscription_lang, inscription_format, inscription_position, use_library_only,
                            use_seal, use_watermark,
                            theme, log):
        """后期处理流水线（全参数版）"""
        try:
            from PIL import Image
            if image.mode != 'RGBA': image = image.convert('RGBA')

            # 1. 装裱
            if composition and composition != "无 (仅画心)":
                try:
                    comp_map = {"立轴 (9:16)": "vertical", "横卷 (16:9)": "horizontal", "屏风 (4:3)": "byobu", "团扇 (1:1)": "fan"}
                    from services.scroll_composer import ScrollComposer
                    composer = ScrollComposer()
                    image = composer.compose(image, comp_map.get(composition, "vertical"))
                    log.append(f"🖼️ 装裱完成: {composition}")
                except Exception as e: log.append(f"⚠️ 装裱失败: {e}")

            # 2. 题词 (使用新参数)
            if use_inscription:
                try:
                    from forgecore.post_process.inscription_generator import InscriptionGenerator
                    from compose_artwork import InscriptionRenderer # 注意：如果这里报错，请改回 from forgecore.post_process.inscription_renderer import InscriptionRenderer
                    
                    ig = InscriptionGenerator()
                    backend = "library" if use_library_only else "auto"
                    
                    text, _ = ig.generate(
                        theme=theme, 
                        format=inscription_format, 
                        return_meta=True, 
                        language=inscription_lang if inscription_lang != "auto" else None,
                        backend=backend
                    )
                    
                    if text:
                        w, h = image.size
                        renderer = InscriptionRenderer()
                        image = renderer.render(
                            image, text, 
                            font_size=max(24, int(min(w, h) * 0.045)), 
                            position=inscription_position # 这里使用了新参数，不再报错
                        )
                        log.append(f"🖌️ 题词完成 [{inscription_format} @ {inscription_position}]")
                except Exception as e: 
                    log.append(f"⚠️ 题词失败: {e}")

            # 3. 印章
            if use_seal:
                try:
                    from forgecore.post_process.seal_generator import SealGenerator
                    sg = SealGenerator()
                    image = sg.apply_scheme(image, "東方藝術", scheme="default")
                    log.append("🔴 印章完成")
                except Exception as e: log.append(f"⚠️ 印章失败: {e}")

            # 4. 做旧 (使用新参数)
            if use_aging:
                try:
                    from forgecore.post_process.aging_processor import AgingProcessor
                    aging = AgingProcessor()
                    tex = aging_texture if aging_texture != "none" else None
                    image = aging.apply(image.convert("RGB"), texture=tex, strength=float(aging_strength))
                    image = image.convert("RGBA")
                    log.append(f" 做旧完成 (强度:{aging_strength})")
                except Exception as e: log.append(f"⚠️ 做旧失败: {e}")

            # 5. 水印
            if use_watermark:
                try:
                    from forgecore.post_process.watermark import WatermarkProcessor
                    wp = WatermarkProcessor()
                    image = wp.add_subtle_watermark(image.convert("RGB"), "ArtForge", opacity=30)
                    image = image.convert("RGBA")
                    log.append("💧 水印完成")
                except Exception as e: log.append(f"⚠️ 水印失败: {e}")

            return image
        except Exception as e:
            log.append(f"❌ 后期处理整体失败: {e}")
            return image
            



    def _apply_post_process(self, image, composition,
                            use_aging, aging_strength, aging_texture,
                            use_inscription, inscription_lang, inscription_format, inscription_position, use_library_only,
                            use_seal, use_watermark,save_clean_copy, 
                            theme, log):
        """后期处理流水线 (修正顺序：先题词印章，再装裱)"""
        try:
            from PIL import Image
            if image.mode != 'RGBA': image = image.convert('RGBA')

            # 1. 题词 (先盖在画心上)
            if use_inscription:
                try:
                    from forgecore.post_process.inscription_generator import InscriptionGenerator
                    from compose_artwork import InscriptionRenderer
                    
                    ig = InscriptionGenerator()
                    backend = "library" if use_library_only else "auto"
                    
                    text, _ = ig.generate(
                        theme=preset_name, 
                        format=inscription_format, 
                        return_meta=True, 
                        language=inscription_lang if inscription_lang != "auto" else None,
                        backend=backend
                    )
                    
                    if text:
                        w, h = image.size
                        renderer = InscriptionRenderer()
                        image = renderer.render(
                            image, text, 
                            font_size=max(24, int(min(w, h) * 0.045)), 
                            position=inscription_position
                        )
                        log.append(f"️ 题词完成 [{inscription_format} @ {inscription_position}] (模式:{backend})")
                except Exception as e: log.append(f"️ 题词失败: {e}")

            # 2. 印章 (盖在画心上)
            if use_seal:
                try:
                    from forgecore.post_process.seal_generator import SealGenerator
                    sg = SealGenerator()
                    image = sg.apply_scheme(image, "東方藝術", scheme="default")
                    log.append("🔴 印章完成")
                except Exception as e: log.append(f"⚠️ 印章失败: {e}")

            # 3. 装裱 (把画心+题词+印章一起装裱)
            if composition and composition != "无 (仅画心)":
                try:
                    comp_map = {"立轴 (9:16)": "vertical", "横卷 (16:9)": "horizontal", "屏风 (4:3)": "byobu", "团扇 (1:1)": "fan"}
                    from services.scroll_composer import ScrollComposer
                    composer = ScrollComposer()
                    image = composer.compose(image, comp_map.get(composition, "vertical"))
                    log.append(f"🖼️ 装裱完成: {composition}")
                except Exception as e: log.append(f"⚠️ 装裱失败: {e}")

            # 4. 做旧 (装裱后做旧，让裱边也有纹理)
            if use_aging:
                try:
                    from forgecore.post_process.aging_processor import AgingProcessor
                    aging = AgingProcessor()
                    tex = aging_texture if aging_texture != "none" else None
                    image = aging.apply(image.convert("RGB"), texture=tex, strength=float(aging_strength))
                    image = image.convert("RGBA")
                    log.append(f"📜 做旧完成 (纹理:{aging_texture}, 强度:{aging_strength})")
                except Exception as e: log.append(f"⚠️ 做旧失败: {e}")

            # 5. 水印(关键修改：在这里复制一份留底图)
            clean_image = None
            if use_watermark:
                # 如果用户勾选了“同时保存无水印留底版”，在加水印前复制当前状态
                if save_clean_copy:
                    clean_image = image.copy() 
                    log.append("🔒 已生成无水印留底副本")            
                try:
                    from forgecore.post_process.watermark import WatermarkProcessor
                    wp = WatermarkProcessor()
                    image = wp.add_subtle_watermark(image.convert("RGB"), "ArtForge", opacity=30)
                    image = image.convert("RGBA")
                    log.append("💧 水印完成")
                except Exception as e: log.append(f"⚠️ 水印失败: {e}")

            #  返回两个值：(最终图, 留底图)
            return image, clean_image
        except Exception as e:
            log.append(f"❌ 后期处理整体失败: {e}")
            return image, None
        
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
    app = ArtForgeApp()
    return app.build_ui()

if __name__ == "__main__":
    demo = build_ui()
    demo.launch(inbrowser=True, share=False)