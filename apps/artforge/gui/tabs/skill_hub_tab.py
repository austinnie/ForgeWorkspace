# apps/artforge/gui/tabs/skill_hub_tab.py
"""技能中心 Tab — 统一调用 forgecore.skills 下所有 skill"""

import json
from pathlib import Path

import gradio as gr

from forgecore.skills.manager import skill_manager
from forgecore.skills.meta_utils import (
    load_meta,
    build_default_params,
    format_info_md,
)


def build_skill_hub_tab(app) -> None:
    SKILLS_DIR = Path(__file__).resolve().parents[3] / "forgecore" / "skills"

    with gr.Row():
        with gr.Column(scale=1):
            all_skills = skill_manager.list_skills()
            skill_names = sorted([s["name"] for s in all_skills])
            skill_info_map = {s["name"]: s for s in all_skills}

            skill_dd = gr.Dropdown(
                choices=skill_names,
                value=skill_names[0] if skill_names else None,
                label=f"选择技能 (共 {len(skill_names)} 个)",
                interactive=True,
            )
            params_input = gr.Code(
                label="参数 (JSON)", language="json", value="{}", lines=12,
            )
            with gr.Row():
                reset_btn = gr.Button("↺ 重置为默认", size="sm")
                run_btn = gr.Button("🚀 执行", variant="primary", size="sm")

        with gr.Column(scale=1):
            info_md = gr.Markdown("### 选择技能后显示说明")
            log_output = gr.Textbox(label="日志", lines=8)
            result_output = gr.JSON(label="结果")

    def on_skill_change(skill_name):
        meta = load_meta(SKILLS_DIR, skill_name)
        skill_meta = skill_info_map.get(skill_name, {})
        default_params = build_default_params(meta)
        default_json = json.dumps(default_params, ensure_ascii=False, indent=2)
        info = format_info_md(skill_name, meta, skill_meta)
        return default_json, info

    skill_dd.change(fn=on_skill_change, inputs=skill_dd, outputs=[params_input, info_md])

    if skill_names:
        init_json, init_info = on_skill_change(skill_names[0])
        params_input.value = init_json
        info_md.value = init_info

    reset_btn.click(fn=on_skill_change, inputs=skill_dd, outputs=[params_input, info_md])

    def execute_skill(skill_name, json_str):
        logs = [f"🚀 执行 skill: {skill_name}"]
        try:
            params = json.loads(json_str) if json_str.strip() else {}
        except json.JSONDecodeError as e:
            return f"❌ JSON 格式错误: {e}", {"error": str(e)}
        except Exception as e:
            return f"❌ 解析参数失败: {e}", {"error": str(e)}

        logs.append(f"📋 参数: {json.dumps(params, ensure_ascii=False)[:200]}")

        try:
            result = skill_manager.run(skill_name, **params)
            status = result.get("status", "unknown")
            logs.append(f"✅ 状态: {status}")
            if result.get("error"):
                logs.append(f"❌ 错误: {result['error']}")
            return "\n".join(logs), result
        except Exception as e:
            import traceback
            logs.append(f"❌ 执行异常: {e}")
            logs.append(traceback.format_exc())
            return "\n".join(logs), {"error": str(e)}

    run_btn.click(
        fn=execute_skill,
        inputs=[skill_dd, params_input],
        outputs=[log_output, result_output],
    )