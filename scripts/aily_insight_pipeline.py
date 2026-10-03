#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Daily Insight Pipeline - 每日行业研报自动生成与发布流水线
参考 amway_daily.py 和 ai_mv.py 的架构，组合 5 个核心 Skills。

功能流程：
1. 资讯抓取 (news_aggregator) -> 2. 研报撰写 (novel_writer) -> 
3. 封面生成 (sd_image_generator) -> 4. 微信排版 (wechat_formatter) -> 
5. 自动发布 (social_auto_upload)

用法:
python scripts/daily_insight_pipeline.py --topic "AI 绘画" --platform wechat
"""
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

# 1. 路径注入
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# 导入 SkillManager
try:
    from forgecore.skills.manager import skill_manager
except ImportError:
    print("❌ 请先确保 forgecore.skills.manager 可用")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / "output" / "pipeline.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

class DailyInsightPipeline:
    """每日研报流水线 (组合应用核心类)"""

    def __init__(self, topic: str, platform: str = "wechat"):
        self.topic = topic
        self.platform = platform
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.work_dir = PROJECT_ROOT / "output" / "daily_insight" / f"{self.timestamp}_{topic}"
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # 中间产物
        self.news_data = None
        self.article_content = None
        self.cover_image_path = None
        self.html_path = None

    def run(self):
        """执行完整流水线"""
        logger.info("=" * 60)
        logger.info(f"  启动每日研报流水线：{self.topic}")
        logger.info("=" * 60)

        # Step 1: 资讯抓取
        if not self._step1_fetch_news():
            logger.error("❌ 步骤 1 失败，流水线终止")
            return False

        # Step 2: 研报撰写
        if not self._step2_write_report():
            logger.error("❌ 步骤 2 失败，流水线终止")
            return False

        # Step 3: 封面生成
        # 注意：图片生成耗时，这里设为可选，失败不阻断流程
        self._step3_generate_cover()

        # Step 4: 微信排版
        if not self._step4_format_wechat():
            logger.error("❌ 步骤 4 失败，流水线终止")
            return False

        # Step 5: 自动发布
        if not self._step5_publish():
            logger.error("❌ 步骤 5 失败，但文件已生成，请手动发布")
            return False

        logger.info("🎉 流水线执行完毕！")
        return True

    def _step1_fetch_news(self) -> bool:
        """步骤 1：抓取最新资讯"""
        logger.info("📡 [Step 1/5] 正在抓取资讯...")
        try:
            res = skill_manager.run(
                "news_aggregator",
                query=self.topic,
                limit=5,
                language="zh"
            )
            if res.get("status") == "success":
                self.news_data = res["result"].get("news_list", [])
                logger.info(f"✅ 抓取成功，共 {len(self.news_data)} 条资讯")
                return True
            else:
                logger.error(f"⚠️ 抓取失败：{res.get('error')}")
                return False
        except Exception as e:
            logger.exception(f"❌ 步骤 1 异常：{e}")
            return False

    def _step2_write_report(self) -> bool:
        """步骤 2：基于资讯撰写研报"""
        logger.info("✍️ [Step 2/5] 正在撰写研报...")
        try:
            # 将新闻列表转化为上下文
            context = "\n".join([f"- {n.get('title', '')}: {n.get('summary', '')}" for n in self.news_data])
            
            res = skill_manager.run(
                "novel_writer",  # 复用小说/文章生成技能
                topic=f"{self.topic} 行业日报",
                context=context,
                style="professional",
                length="medium"
            )
            if res.get("status") == "success":
                self.article_content = res["result"].get("content", "")
                # 保存草稿
                draft_path = self.work_dir / "draft.md"
                draft_path.write_text(self.article_content, encoding="utf-8")
                logger.info(f"✅ 撰写成功，已保存至 {draft_path}")
                return True
            else:
                logger.error(f"⚠️ 撰写失败：{res.get('error')}")
                return False
        except Exception as e:
            logger.exception(f"❌ 步骤 2 异常：{e}")
            return False

    def _step3_generate_cover(self):
        """步骤 3：生成封面图 (异步/可选)"""
        logger.info("🎨 [Step 3/5] 正在生成封面图...")
        try:
            res = skill_manager.run(
                "sd_image_generator",
                prompt=f"{self.topic}, futuristic, high quality, cover art",
                negative_prompt="worst quality, lowres",
                batch_size=1,
                output_dir=str(self.work_dir)
            )
            if res.get("status") == "success":
                imgs = res["result"].get("image_paths", [])
                if imgs:
                    self.cover_image_path = imgs[0]
                    logger.info(f"✅ 封面生成成功：{self.cover_image_path}")
        except Exception as e:
            logger.warning(f"️ 封面生成跳过：{e}")

    def _step4_format_wechat(self) -> bool:
        """步骤 4：微信排版"""
        logger.info("📐 [Step 4/5] 正在进行微信排版...")
        try:
            res = skill_manager.run(
                "wechat_formatter",
                content=self.article_content,
                title=f"【日报】{self.topic} 最新动态 ({self.timestamp})",
                cover_image=str(self.cover_image_path) if self.cover_image_path else None,
                theme="tech_blue"
            )
            if res.get("status") == "success":
                self.html_path = self.work_dir / "final.html"
                self.html_path.write_text(res["result"].get("html", ""), encoding="utf-8")
                logger.info(f"✅ 排版成功，已保存至 {self.html_path}")
                return True
            else:
                logger.error(f"⚠️ 排版失败：{res.get('error')}")
                return False
        except Exception as e:
            logger.exception(f"❌ 步骤 4 异常：{e}")
            return False

    def _step5_publish(self) -> bool:
        """步骤 5：自动发布"""
        logger.info(f"🚀 [Step 5/5] 正在发布至 {self.platform}...")
        try:
            res = skill_manager.run(
                "social_auto_upload",
                platform=self.platform,
                file=str(self.html_path),
                title=f"{self.topic} 日报",
                desc=f"自动生成：{self.topic} 行业最新动态",
                tags=[self.topic, "AI", "日报"]
            )
            if res.get("status") == "success":
                logger.info("✅ 发布成功！")
                return True
            else:
                logger.error(f"️ 发布失败：{res.get('error')}")
                return False
        except Exception as e:
            logger.exception(f"❌ 步骤 5 异常：{e}")
            return False

import random

class AutoTopicSelector:
    """自动主题选择器"""
    def __init__(self, pool_file: str):
        self.pool_file = Path(pool_file)
        if not self.pool_file.exists():
            self.pool_file.parent.mkdir(parents=True, exist_ok=True)
            self.pool_file.write_text("AI 绘画\nSora 视频\n", encoding="utf-8") # 默认兜底

    def get_random_topic(self) -> str:
        """从池中随机选一个"""
        lines = self.pool_file.read_text(encoding="utf-8").strip().split('\n')
        lines = [l.strip() for l in lines if l.strip()]
        if not lines:
            return "AI 行业日报" # 兜底
        return random.choice(lines)

    def get_queue_topic(self) -> str:
        """从队列文件取第一个（适合每日按顺序执行）"""
        queue_file = self.pool_file.parent / "topic_queue.txt"
        if not queue_file.exists():
            return self.get_random_topic()
        
        lines = queue_file.read_text(encoding="utf-8").strip().split('\n')
        lines = [l.strip() for l in lines if l.strip()]
        
        if not lines:
            return "AI 行业日报"
            
        # 取出第一个
        topic = lines[0]
        # 移到已完成文件
        done_file = self.pool_file.parent / "topic_done.txt"
        with open(done_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d')}: {topic}\n")
        
        # 更新队列
        with open(queue_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines[1:]))
            
        return topic
        
def main():
    parser = argparse.ArgumentParser(description="每日研报自动生成流水线")
    parser.add_argument("--topic", default=None, help="指定主题 (不填则自动)")
    parser.add_argument("--mode", default="random", choices=["random", "queue"], help="自动模式：random=随机, queue=按顺序")
    parser.add_argument("--platform", default="wechat", help="发布平台")
    args = parser.parse_args()

    #  核心：如果没有指定 topic，则自动选择
    final_topic = args.topic
    if not final_topic:
        selector = AutoTopicSelector(PROJECT_ROOT / "data" / "topics_pool.txt")
        if args.mode == "queue":
            final_topic = selector.get_queue_topic()
            print(f"📅 [队列模式] 自动选择今日主题: {final_topic}")
        else:
            final_topic = selector.get_random_topic()
            print(f"🎲 [随机模式] 自动选择主题: {final_topic}")

    pipeline = DailyInsightPipeline(topic=final_topic, platform=args.platform)
    success = pipeline.run()
    
    if not success:
        sys.exit(1)