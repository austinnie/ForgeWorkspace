# apps/promptforge/router_test.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PromptForge 技能路由演示"""
import sys
from pathlib import Path

# 注入 ForgeCore
CORE_PATH = Path(__file__).resolve().parent.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

# 模拟 PromptForge 的技能路由表 (提取自旧版 core/skill_routes.py)
SKILL_ROUTES = {
    "image_generator": {"keywords": ["画图", "生成图片", "画一张", "文生图"]},
    "github_repo_daily": {"keywords": ["github推荐", "github仓库", "trending", "开源项目"]},
    "daily_pipeline": {"keywords": ["日更", "生成文章", "排版", "公众号"]},
    "video_generator": {"keywords": ["生成视频", "做个视频", "文生视频"]},
    "news_aggregator": {"keywords": ["新闻", "热点", "今日简报"]},
}

def match_skill(user_input: str) -> str:
    """简单的关键词路由匹配"""
    for skill_name, config in SKILL_ROUTES.items():
        for kw in config["keywords"]:
            if kw in user_input:
                return skill_name
    return "chat" # 默认闲聊

def main():
    print("=" * 50)
    print("📝 PromptForge 技能路由演示")
    print("=" * 50 + "\n")
    
    test_inputs = [
        "帮我画一张赛博朋克风格的机甲少女",
        "今天 github 有什么推荐的开源项目？",
        "帮我生成一篇关于 AI 的文章并排版发公众号",
        "给我看看今天的科技热点新闻",
        "你好，今天天气怎么样？",
    ]
    
    for text in test_inputs:
        skill = match_skill(text)
        print(f"🗣️ 用户: {text}")
        print(f"🎯 路由: [{skill}]")
        print("-" * 40)

if __name__ == "__main__":
    main()