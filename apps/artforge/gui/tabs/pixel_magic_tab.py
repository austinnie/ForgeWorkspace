# apps/artforge/gui/tabs/pixel_magic_tab.py
"""像素魔法 Tab — 一键像素编辑"""

from pathlib import Path

import gradio as gr

from forgecore.config.registry import ModelRegistry
from forgecore.skills.manager import skill_manager
from forgecore.image.temp_utils import pil_to_temp_png, safe_remove
from forgecore.image.saver import save_image
from forgecore.skills.result_utils import extract_skill_image
from forgecore.engines.helpers import agnes_img2img


PIXEL_SKILLS = [
    "add_glasses", "add_tattoo", "add_animal_ears", "add_background_objects",
    "change_hair", "change_age", "change_gender", "change_body_type", "change_expression",
    "change_eye_color", "change_makeup", "change_skin_tone", "change_nationality", "change_face",
    "change_clothes", "change_clothing_style", "remove_clothes",
    "change_pose", "change_perspective", "expand_to_full_body",
    "change_background", "change_furniture", "change_lighting", "day_night_transfer",
    "season_transfer", "weather_transfer",
    "remove_object", "replace_object",
    "anime_to_real", "real_to_anime", "style_transfer", "sketch_to_real",
    "colorize_sketch", "photo_realistic",
    "fix_human_anatomy", "mosaic_reducer", "old_photo_restore", "photo_restorer",
    "human_to_robot", "fantasy_character", "mecha_generator",
    "intimate_closeup", "bathroom_nude", "beach_lingerie", "bedroom_lingerie",
    "bedroom_nude", "pool_nude", "studio_nude", "nude_oil_painting", "nude_sculpture",
]

PROMPT_MAP = {
    "add_glasses": "wearing elegant glasses, sophisticated, masterpiece",
    "add_tattoo": "with beautiful tattoo on skin, artistic, masterpiece",
    "change_hair": "different hairstyle, detailed hair, masterpiece",
    "change_background": "beautiful new background, scenic, masterpiece",
    "remove_object": "clean background, no objects, masterpiece",
}


def build_pixel_magic_tab(app) -> None:
    with gr.Row():
        with gr.Column(scale=1):
            magic_skill_dd = gr.Dropdown(
                choices=PIXEL_SKILLS, value="add_glasses", label="✨ 选择魔法技能"
            )
            magic_ref_image = gr.Image(
                label="📎 上传参考图 (必须)", type="pil", height=300
            )
            magic_engine_mode = gr.Radio(
                choices=[("☁️ Agnes API (模拟)", "agnes"), ("💻 本地模型 (推荐)", "local")],
                value="local", label="生成引擎",
            )
            local_models = [m["name"] for m in ModelRegistry.scan_checkpoints("sd15")]
            magic_local_model = gr.Dropdown(
                choices=local_models,
                label="本地模型",
                value=local_models[0] if local_models else None,
            )
            magic_btn = gr.Button("✨ 施展魔法", variant="primary", size="lg")

        with gr.Column(scale=1):
            magic_out = gr.Image(label="✨ 结果", type="pil", height=400)
            magic_log = gr.Textbox(label="日志", lines=10)

    def run_pixel_magic(skill_name, ref_img, mode, model_name):
        logs = [f"✨ 启动: {skill_name}"]
        if ref_img is None:
            return None, "❌ 必须上传参考图！"

        try:
            final_image = None

            if mode == "agnes":
                logs.append(f"☁️ 使用 Agnes API 模拟 {skill_name}...")
                sim_prompt = PROMPT_MAP.get(
                    skill_name, f"{skill_name.replace('_', ' ')}, masterpiece"
                )
                from gui.common import load_env_config
                final_image = agnes_img2img(
                    prompt=sim_prompt,
                    image=ref_img,
                    strength=0.6,
                    width=768, height=1024,
                    config=load_env_config(),
                )
                logs.append("✅ Agnes API 模拟执行成功")

            else:
                if not model_name:
                    return None, "❌ 请选择本地模型"
                model_obj = next(
                    (m for m in ModelRegistry.scan_checkpoints("sd15")
                     if m["name"] == model_name),
                    None,
                )
                if not model_obj:
                    return None, "❌ 找不到模型"

                temp_img_path = pil_to_temp_png(ref_img)
                logs.append(f"📂 图片暂存: {Path(temp_img_path).name}")
                output_path = temp_img_path.replace(".png", f"_{skill_name}_out.png")
                kwargs = {
                    "image_path": temp_img_path,
                    "output_path": output_path,
                    "model_path": model_obj["absolute_path"],
                }
                logs.append(f"📂 模型: {model_name}")

                res = skill_manager.run(skill_name, **kwargs)
                final_image = extract_skill_image(res)

                if final_image is None and "unexpected keyword argument" in str(res.get("error", "")):
                    logs.append("🔄 降级重试...")
                    kwargs.pop("output_path", None)
                    res = skill_manager.run(skill_name, **kwargs)
                    final_image = extract_skill_image(res)

                if final_image is not None:
                    logs.append("✅ 本地技能执行成功")
                else:
                    logs.append(f"❌ 本地技能失败: {res.get('error')}")

                safe_remove(temp_img_path)

            if final_image:
                save_path = save_image(final_image, prefix=f"magic_{skill_name}")
                if save_path:
                    logs.append(f"💾 已保存: {save_path}")
                return final_image, "\n".join(logs)

            return None, "\n".join(logs) + "\n❌ 未能生成图片"

        except Exception as e:
            return None, f"❌ 错误: {e}"

    magic_btn.click(
        fn=run_pixel_magic,
        inputs=[magic_skill_dd, magic_ref_image, magic_engine_mode, magic_local_model],
        outputs=[magic_out, magic_log],
    )