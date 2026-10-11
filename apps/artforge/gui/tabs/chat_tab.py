# apps/artforge/gui/tabs/chat_tab.py
"""对话生图 Tab — 自然语言 → 自动路由 → 出图"""

import os

import gradio as gr

from forgecore.skills.manager import skill_manager


def build_chat_tab(app) -> None:
    chat_state = {"history": []}

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 💬 自然语言生成 / 编辑")
            gr.Markdown(
                "**例子**：画一只猫 / 加猫耳 / 换成红色裙子 / "
                "把背景换成樱花 / 转成油画风格 / 老照片修复"
            )

            msg_input = gr.Textbox(
                label="你想做什么？",
                placeholder="例如：画一只坐在窗台上的猫，阳光洒落",
                lines=3,
            )
            ref_image = gr.Image(
                label="参考图 (可选，用于图生图)",
                type="filepath",
                height=200,
            )
            conv_id = gr.Textbox(
                label="会话 ID",
                value="default",
                info="相同 ID 的对话会记住上下文（多轮编辑）",
            )

            with gr.Row():
                send_btn = gr.Button("🚀 发送", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ 清空历史", size="lg")

            with gr.Accordion("⚙️ 高级参数", open=False):
                use_api_cb = gr.Checkbox(label="使用 API 出图（Agnes，快）", value=True)
                llm_model = gr.Dropdown(
                    choices=["agnes-2.5-flash"],
                    value="agnes-2.5-flash",
                    label="LLM 模型",
                )

        with gr.Column(scale=2):
            response_box = gr.Textbox(label="AI 回复", lines=4, interactive=False)
            result_image = gr.Image(label="生成结果", type="filepath", height=500)
            with gr.Accordion("🔍 详细结果 (JSON)", open=False):
                detail_json = gr.JSON(label="完整返回")
            with gr.Accordion("📜 对话历史", open=False):
                history_box = gr.Textbox(label="", lines=10, interactive=False)

    def on_send(message, ref_img, conv, use_api, model):
        if not message or not message.strip():
            return "⚠️ 请输入内容", None, {}, ""

        skill_manager.scan()

        kwargs = {
            "message": message.strip(),
            "conversation_id": conv or "default",
        }
        if ref_img:
            kwargs["image_path"] = ref_img

        kwargs["model"] = model
        kwargs["api_type"] = "openai_compatible"
        kwargs["api_base"] = "https://apihub.agnes-ai.com/v1"
        kwargs["api_key"] = os.getenv("AGNES_API_KEY", "")

        try:
            result = skill_manager.run("chattoimage", **kwargs)
        except Exception as e:
            import traceback
            return f"❌ 执行异常: {e}\n{traceback.format_exc()}", None, {}, ""

        status = result.get("status", "unknown")
        if status == "success":
            reply = result.get("response", "(无回复)")
            paths = result.get("image_paths", [])
            img = paths[0] if paths else None

            chat_state["history"].append({"user": message, "ai": reply, "image": img})
            history_text = "\n\n".join([
                f"👤 {h['user']}\n🤖 {h['ai']}"
                for h in chat_state["history"][-10:]
            ])
            return reply, img, result, history_text
        else:
            err = result.get("error", "未知错误")
            return f"❌ {err}", None, result, ""

    def on_clear():
        chat_state["history"] = []
        return "", None, {}, ""

    send_btn.click(
        fn=on_send,
        inputs=[msg_input, ref_image, conv_id, use_api_cb, llm_model],
        outputs=[response_box, result_image, detail_json, history_box],
    )
    clear_btn.click(
        fn=on_clear,
        inputs=[],
        outputs=[response_box, result_image, detail_json, history_box],
    )
    msg_input.submit(
        fn=on_send,
        inputs=[msg_input, ref_image, conv_id, use_api_cb, llm_model],
        outputs=[response_box, result_image, detail_json, history_box],
    )