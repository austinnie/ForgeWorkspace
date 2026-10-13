# apps/artforge/gui/tabs/generation_tab.py
"""生图 Tab — 主题与预设 / 引擎 / 参数 / 后期处理"""

from typing import Optional

import gradio as gr


def build_generation_tab(app) -> None:
    """app 是 ArtForgeApp 实例。
    需要 app.available_libs / app.current_lib / app.categories /
    app.preset_engine / app.template_manager / app.loras /
    app._get_models / app._build_prompt_from_preset / app._generate_image
    """
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group():
                gr.Markdown("###  主题与预设")

                gr.Markdown("**📁 Python 预设** (presets_by_app)")
                preset_library_dd = gr.Dropdown(
                    choices=app.available_libs,
                    value=app.current_lib,
                    label=" 预设库 (Preset Library)",
                )
                category_dd = gr.Dropdown(
                    choices=app.categories,
                    value=(app.categories[0] if app.categories else None),
                    label="主题分类 (Category)",
                )

                _first_cat = app.categories[0] if app.categories else None
                _first_presets = (
                    app.preset_engine.list_preset_names(app.current_lib, _first_cat)
                    if (app.preset_engine and _first_cat) else []
                )
                preset_dd = gr.Dropdown(
                    choices=_first_presets,
                    value=(_first_presets[0] if _first_presets else None),
                    label="预设场景 (Preset)",
                )

                gr.Markdown("**📚 JSON 模板** (templates/sd_gui)")
                template_cat_dd = gr.Dropdown(
                    choices=app.template_manager.list_categories() if app.template_manager else [],
                    value=(app.template_manager.list_categories()[0]
                           if app.template_manager and app.template_manager.categories else None),
                    label="模板分类 (Template Category)",
                )
                _first_template_items = (
                    app.template_manager.get_items(app.template_manager.list_categories()[0])
                    if app.template_manager and app.template_manager.categories else []
                )
                template_item_dd = gr.Dropdown(
                    choices=[it["name"] for it in _first_template_items],
                    value=(_first_template_items[0]["name"] if _first_template_items else None),
                    label="模板项目 (Template Item)",
                )
                template_load_btn = gr.Button("⬇️ 加载模板到提示词", size="sm")

                prompt_input = gr.Textbox(
                    label="正向提示词 (Prompt)", lines=4,
                    placeholder="由预设或模板自动生成...",
                )
                negative_input = gr.Textbox(
                    label="负向提示词", lines=2,
                    value="worst quality, low quality, ugly, deformed, blurry, bad anatomy, watermark, text",
                )

            with gr.Group():
                gr.Markdown("### 🔌 引擎选择")
                engine_mode = gr.Radio(
                    choices=[("☁️ API 引擎", "api"), ("💻 本地模型", "local")],
                    value="api", label="生成模式",
                )
                api_provider = gr.Dropdown(
                    choices=["pollinations", "agnes", "siliconflow", "tongyi", "yige", "hunyuan","openrouter", "orcarouter"],
                    value="agnes", label="API 提供商",
                )
                
                # ===== 新增：OrcaRouter 模型选择（默认隐藏）=====
                with gr.Group(visible=False) as orcarouter_config:
                    orcarouter_model_dd = gr.Dropdown(
                        choices=[
                            "openai/gpt-4o-mini (推荐)",
                            "openai/gpt-4o",
                            "anthropic/claude-opus-4.6",
                            "anthropic/claude-sonnet-4.6",
                            "google/gemini-2.5-pro",
                            "deepseek/deepseek-v4-flash",
                            "xai/grok-3",
                            "qwen/qwen3.7-max",
                            "kling/kling-v3-omni",
                            "byteplus/dreamina-seedance-2-0-260128",
                        ],
                        value="openai/gpt-4o-mini (推荐)",
                        label="OrcaRouter 模型",
                    )  
                    
                with gr.Group(visible=False) as local_config:
                    model_type_dd = gr.Dropdown(
                        choices=["SD1.5", "SDXL"], value="SD1.5", label="模型类型"
                    )
                    model_dd = gr.Dropdown(
                        choices=app._get_models("sd15"), label="选择主模型"
                    )
                    refresh_model_btn = gr.Button(" 刷新模型", size="sm")

            with gr.Group(visible=False) as lora_group:
                gr.Markdown("###  LoRA 扩展")
                lora_dd = gr.Dropdown(
                    choices=[l["name"] for l in app.loras],
                    label="选择 LoRA", allow_custom_value=True,
                )
                lora_weight = gr.Slider(
                    minimum=0.0, maximum=1.5, value=0.7, step=0.1, label="LoRA 权重"
                )

            with gr.Group():
                gr.Markdown("### ⚙️ 高级参数")
                with gr.Row():
                    steps_slider = gr.Slider(minimum=10, maximum=50, value=15, step=1, label="采样步数 (Steps)")
                    cfg_slider = gr.Slider(minimum=1.0, maximum=15.0, value=7.5, step=0.5, label="CFG Scale")
                with gr.Row():
                    seed_input = gr.Number(value=-1, label="种子 (Seed, -1 为随机)", precision=0)
                    count_slider = gr.Slider(minimum=1, maximum=4, value=1, step=1, label="生成数量 (Batch Size)")

            with gr.Group():
                gr.Markdown("### ️ 后期处理与装裱")
                composition_dd = gr.Dropdown(
                    choices=["无 (仅画心)", "立轴 (9:16)", "横卷 (16:9)", "屏风 (4:3)", "团扇 (1:1)"],
                    value="立轴 (9:16)", label="装裱方式",
                )
                with gr.Row():
                    use_aging_cb = gr.Checkbox(label="启用古画做旧", value=False, scale=1)
                    use_inscription_cb = gr.Checkbox(label="启用竖排题词", value=True, scale=1)
                    use_seal_cb = gr.Checkbox(label="启用印章", value=True, scale=1)
                    seal_texture_dd = gr.Dropdown(
                        choices=[("平面 (Flat)", "flat"), ("石刻 (Stone)", "stone")],
                        value="flat", label="印章质感", scale=1,
                    )
                with gr.Accordion("📜 做旧高级设置", open=False):
                    with gr.Row():
                        aging_strength = gr.Slider(
                            minimum=0.1, maximum=1.0, value=0.5, step=0.1,
                            label="做旧强度 (0.1=轻微泛黄, 1.0=重度破损)", scale=2,
                        )
                        aging_texture = gr.Dropdown(
                            choices=["xuan_paper", "silk", "aged", "brown", "none"],
                            value="xuan_paper", label="纸张纹理类型 (none=无纹理)", scale=1,
                        )
                with gr.Accordion("🖌️ 题词高级设置", open=False):
                    with gr.Row():
                        inscription_language_dd = gr.Dropdown(
                            choices=[
                                ("自动 (Auto)", "auto"),
                                ("中文 (Chinese)", "chinese"),
                                ("日文 (Japanese)", "japanese"),
                                ("英文 (English)", "english"),
                            ],
                            value="auto", label="题词语言", scale=1,
                        )
                        inscription_format_dd = gr.Dropdown(
                            choices=[
                                ("自动 (Auto)", "auto"),
                                ("五言绝句 (20字)", "wuyan"),
                                ("七言绝句 (28字)", "qiyan"),
                                ("和歌 (Waka)", "waka"),
                                ("俳句 (Haiku)", "haiku"),
                                ("题跋 (散文)", "tiba"),
                            ],
                            value="auto", label="题词体裁 (Format)", scale=1,
                        )
                        inscription_position_dd = gr.Dropdown(
                            choices=[
                                ("右上题诗 (Top Right)", "top_right"),
                                ("左下落款 (Bottom Left)", "bottom_left"),
                                ("左上角 (Top Left)", "top_left"),
                            ],
                            value="top_right", label="题词位置 (Position)", scale=1,
                        )
                    with gr.Row():
                        use_library_only_cb = gr.Checkbox(
                            label="仅用内置诗句库 (离线/秒出，不调用 AI)", value=False
                        )
                with gr.Row():
                    use_watermark_cb = gr.Checkbox(label="隐形水印", value=False, scale=1)
                    save_clean_copy_cb = gr.Checkbox(
                        label="同时保存无水印留底版 (自己收藏)", value=False
                    )
                    use_appraise_cb = gr.Checkbox(label="AI 自动鉴赏 (BLIP)", value=False, scale=1)

            generate_btn = gr.Button("🎨 开始生成", variant="primary", size="lg")

        with gr.Column(scale=2):
            output_image = gr.Image(label="生成结果 (分享版)", type="filepath", height=700)
            output_image_clean = gr.Image(
                label="无水印留底版 (自己收藏)", type="filepath",
                height=700, visible=False,
            )
            output_info = gr.Textbox(label="执行日志", lines=12)

    # ========== 事件绑定 ==========
    def on_provider_change(provider):
        is_orcarouter = (provider == "orcarouter")
        return gr.update(visible=is_orcarouter)

    api_provider.change(
        fn=on_provider_change,
        inputs=api_provider,
        outputs=orcarouter_config,
    )
    
    def on_orcarouter_model_change(model_value):
        """当用户选择 OrcaRouter 模型时，更新 app 实例的模型配置"""
        if hasattr(app, 'orcarouter_model'):
            app.orcarouter_model = model_value
            print(f"  [OrcaRouter] 模型已切换为: {model_value}")
        return None
    
    orcarouter_model_dd.change(
        fn=on_orcarouter_model_change,
        inputs=orcarouter_model_dd,
    )
    
    def on_lib_change(lib_name):
        app.current_lib = lib_name
        new_cats = app.preset_engine.list_categories(lib_name) if app.preset_engine else []
        app.categories = new_cats
        first_cat = new_cats[0] if new_cats else None
        app.current_category = first_cat
        new_presets = (
            app.preset_engine.list_preset_names(lib_name, first_cat)
            if (app.preset_engine and first_cat) else []
        )
        first_preset = new_presets[0] if new_presets else None
        app.current_preset = first_preset
        return (
            gr.update(choices=new_cats, value=first_cat),
            gr.update(choices=new_presets, value=first_preset),
        )

    preset_library_dd.change(
        fn=on_lib_change, inputs=[preset_library_dd], outputs=[category_dd, preset_dd]
    )

    def on_category_change(cat):
        app.current_category = cat
        names = (
            app.preset_engine.list_preset_names(app.current_lib, cat)
            if app.preset_engine else []
        )
        first = names[0] if names else None
        app.current_preset = first
        return gr.update(choices=names, value=first)

    category_dd.change(fn=on_category_change, inputs=category_dd, outputs=preset_dd)

    def on_preset_change(cat, preset_name):
        app.current_category = cat
        app.current_preset = preset_name
        if not app.preset_engine:
            return ""
        preset = app.preset_engine.load_preset(app.current_lib, cat, preset_name)
        if preset:
            return app._build_prompt_from_preset(preset)
        return ""

    preset_dd.change(fn=on_preset_change, inputs=[category_dd, preset_dd], outputs=prompt_input)

    def on_template_cat_change(cat):
        if not app.template_manager:
            return gr.update(choices=[], value=None)
        items = app.template_manager.get_items(cat)
        names = [it["name"] for it in items]
        return gr.update(choices=names, value=(names[0] if names else None))

    template_cat_dd.change(
        fn=on_template_cat_change, inputs=template_cat_dd, outputs=template_item_dd
    )

    def on_template_load(cat, item_name):
        if not app.template_manager:
            return ""
        items = app.template_manager.get_items(cat)
        target = next((it for it in items if it["name"] == item_name), None)
        if target:
            return target.get("prompt", "")
        return ""

    template_load_btn.click(
        fn=on_template_load,
        inputs=[template_cat_dd, template_item_dd],
        outputs=prompt_input,
    )

    def on_engine_mode_change(mode):
        is_local = (mode == "local")
        return (
            gr.update(visible=not is_local),
            gr.update(visible=is_local),
            gr.update(visible=is_local),
        )

    engine_mode.change(
        fn=on_engine_mode_change,
        inputs=engine_mode,
        outputs=[api_provider, local_config, lora_group],
    )

    def on_refresh_models(m_type):
        key = "sd15" if m_type == "SD1.5" else "sdxl"
        return gr.update(choices=app._get_models(key))

    refresh_model_btn.click(on_refresh_models, inputs=model_type_dd, outputs=model_dd)
    model_type_dd.change(on_refresh_models, inputs=model_type_dd, outputs=model_dd)
    generate_btn.click(
        fn=app._generate_image,
        inputs=[
            engine_mode, api_provider, model_dd,
            category_dd, preset_dd, composition_dd,
            prompt_input, negative_input,
            lora_dd, lora_weight,
            steps_slider, cfg_slider, seed_input, count_slider,
            use_aging_cb, aging_strength, aging_texture,
            use_inscription_cb, inscription_format_dd, inscription_position_dd,
            use_library_only_cb,
            use_seal_cb, use_watermark_cb, save_clean_copy_cb,
            inscription_language_dd, use_appraise_cb,
            seal_texture_dd,
        ],
        outputs=[output_image, output_image_clean, output_info],
    )