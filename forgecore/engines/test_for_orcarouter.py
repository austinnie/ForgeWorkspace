from orcarouter import OrcaRouterEngine, create_orcarouter_engine

# 初始化
api_key = "sk-orca-Je5WBPd82F2LMDIsNNCcguuUWg17REJSFK4exlmpGpA"
engine = create_orcarouter_engine(api_key)

# 1. Chat 对话
response = engine.chat(
    messages=[{"role": "user", "content": "你好"}],
    model="openai/gpt-4o-mini"
)

# 2. 流式对话
for chunk in engine.chat(messages=messages, stream=True):
    print(chunk, end='', flush=True)

# 3. 工具调用
result = engine.chat_tool_call(
    messages=[...],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "parameters": {"type": "object", "properties": {"city": {"type": "string"}}}
        }
    }]
)

# 4. 视觉理解
result = engine.chat_vision("描述这张图片", image_url="https://example.com/image.jpg")

# 5. 图像生成
images = engine.generate_image("一只可爱的猫咪", model="openai/gpt-image-1")

# 6. 文本转语音
audio = engine.text_to_speech("你好世界", voice="alloy")
engine.save_tts("你好世界", "output.mp3")

# 7. Kling 视频生成
task = engine.video_generation(
    prompt="海浪拍打岩石",
    model="kling/kling-v3-omni",
    duration=5,
    aspect_ratio="16:9"
)
video_url = engine.wait_for_video(task['id'])

# 8. Seedance 视频生成
task = engine.video_generation(
    prompt="日落时分的海滩",
    model="byteplus/dreamina-seedance-2-0-260128",
    generate_audio=True
)

# 9. 列出可用模型
models = engine.get_models()

# 10. Seedance 资产组
assets = engine.list_asset_groups(group_type="real_human")