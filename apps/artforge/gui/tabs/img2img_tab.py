# apps/artforge/gui/tabs/img2img_tab.py
"""图生图 & ControlNet Tab"""

from pathlib import Path

import gradio as gr

from forgecore.config.registry import ModelRegistry
from forgecore.skills.manager import skill_manager
from forgecore.config.model_resolver import resolve_model
from forgecore.skills.result_utils import extract_skill_image
from forgecore.image.saver import save_image
from forgecore.engines.helpers import agnes_img2img


def build_img2img_tab(app) -> None:
    gr.Markdown("### 🖼️ 图生图 / ControlNet 工作台")
    gr.Markdown(
        "💡 **核心逻辑**：上传参考图锁定特征，通过提示词引导继续创作。"
        "默认使用 Agnes API 图生图，也支持本地 ControlNet 模型。"
    )

    with gr.Row():
        with gr.Column(scale=1):
            i2i_ref_image = gr.Image(
                label="📎 上传参考图 (Control Source / 图生图底图)",
                type="pil", height=300,
            )
            i2i_engine_mode = gr.Radio(
                choices=[("☁️ Agnes API (图生图)", "agnes"), ("💻 本地模型 (ControlNet)", "local")],
                value="agnes", label="生成引擎",
            )
            local_models = [m["name"] for m in ModelRegistry.scan_checkpoints("sd15")]
            i2i_local_model = gr.Dropdown(
                choices=local_models,
                label="本地模型 (SD1.5) - 仅本地引擎生效",
                value=local_models[0] if local_models else None,
            )
            i2i_prompt = gr.Textbox(
                label="提示词 (Prompt - 描述你想要的变化)",
                value="masterpiece, best quality, detailed face", lines=2,
            )
            i2i_neg = gr.Textbox(
                label="负面提示词 (仅本地模型生效)",
                value="worst quality, lowres, bad anatomy", lines=1,
            )
            with gr.Group():
                gr.Markdown("#### 🎛️ 控制参数")
                i2i_cn_type = gr.Dropdown(
                    choices=["openpose", "canny", "depth", "lineart", "hed", "无 (纯图生图)"],
                    label="ControlNet 类型 / 参考方式", value="无 (纯图生图)",
                )
                i2i_strength = gr.Slider(
                    0.1, 1.0, value=0.6,
                    label="重绘幅度 / ControlNet 强度 (0.1=微调, 1.0=大改)",
                )
            i2i_btn = gr.Button("🚀 开始图生图", variant="primary", size="lg")

        with gr.Column(scale=1):
            i2i_out = gr.Image(label="生成结果", type="pil", height=400)
            i2i_log = gr.Textbox(label="生成日志", lines=10)

    def run_img2img(ref_img, mode, model_name, prompt, negative, cn_type, strength):
        logs = ["🚀 启动图生图 / ControlNet 流水线..."]

        if ref_img is None:
            return None, "❌ 必须上传参考图！图生图/ControlNet 需要底图来锁定特征。"

        try:
            final_image = None

            if mode == "agnes":
                logs.append("☁️ 使用 Agnes API 图生图")
                from gui.common import load_env_config
                final_image = agnes_img2img(
                    prompt=prompt,
                    image=ref_img,
                    strength=strength,
                    width=768, height=1024,
                    config=load_env_config(),
                )
                logs.append("✅ Agnes API 图生图完成")
            else:
                if not model_name:
                    return None, "❌ 选择本地引擎时，必须选择本地模型。"

                model_obj = resolve_model(model_name)
                if not model_obj:
                    return None, "❌ 找不到模型路径"
                model_path = model_obj["absolute_path"]
                logs.append(f"📂 本地模型: {model_name}")

                if cn_type and cn_type != "无 (纯图生图)":
                    logs.append(f"🎛️ 调用本地 ControlNet (类型: {cn_type})")
                    res = skill_manager.run(
                        "controlnet", action="generate", image=ref_img, prompt=prompt,
                        negative_prompt=negative, model_path=model_path,
                        controlnet_type=cn_type, controlnet_conditioning_scale=strength,
                    )
                else:
                    logs.append("🖼️ 调用本地图生图")
                    res = skill_manager.run(
                        "controlnet", action="generate", image=ref_img, prompt=prompt,
                        negative_prompt=negative, model_path=model_path,
                        controlnet_type="canny", controlnet_conditioning_scale=0.0,
                        strength=strength,
                    )

                final_image = extract_skill_image(res)
                if final_image is None:
                    logs.append(f"❌ 本地生成失败: {res.get('error')}")
                else:
                    logs.append("✅ 本地生成成功")

            if final_image is not None:
                save_path = save_image(final_image, prefix="img2img")
                if save_path:
                    logs.append(f"💾 图片已自动保存: {save_path}")
                return final_image, "\n".join(logs)
            else:
                return None, "\n".join(logs) + "\n❌ 未生成有效图片"

        except Exception as e:
            import traceback
            return None, f"❌ 执行出错: {str(e)}\n{traceback.format_exc()}"

    i2i_btn.click(
        fn=run_img2img,
        inputs=[i2i_ref_image, i2i_engine_mode, i2i_local_model, i2i_prompt,
                i2i_neg, i2i_cn_type, i2i_strength],
        outputs=[i2i_out, i2i_log],
    )