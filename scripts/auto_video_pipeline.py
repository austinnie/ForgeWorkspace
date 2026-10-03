#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto Video Pipeline - 自动化视频创作流水线 (ForgeWorkspace 专属版)
参考 ai_mv.py 逻辑，全面接入 SkillManager
用法:
python scripts/auto_video_pipeline.py --topic "敦煌飞天" --count 5 --publish
"""
import sys
import time
import argparse
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# 1. 路径注入
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from forgecore.skills.manager import skill_manager
except ImportError:
    print("❌ 请先确保 forgecore.skills.manager 可用")
    sys.exit(1)

def log_step(step_num, total, title):
    print(f"\n{'='*60}")
    print(f"  步骤 {step_num}/{total}: {title}")
    print(f"{'='*60}")

def run_pipeline(topic: str, count: int, emotion: str, do_publish: bool):
    start_time = time.time()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    work_dir = PROJECT_ROOT / "output" / "pipeline" / f"{ts}_{topic}"
    work_dir.mkdir(parents=True, exist_ok=True)

    # ==========================================
    # Step 1: 批量出图 (调用 sd_image_generator 或 batch_generate 逻辑)
    # ==========================================
    log_step(1, 5, "批量生成图片")
    print(f"  主题: {topic}, 数量: {count}")
    
    res_img = skill_manager.run(
        "sd_image_generator",
        prompt=f"{topic}, masterpiece, best quality, highres, oriental art",
        negative_prompt="worst quality, lowres, bad anatomy",
        batch_size=count,
        output_dir=str(work_dir / "images")
    )
    
    if res_img.get("status") != "success":
        print(f"❌ 出图失败: {res_img.get('error')}")
        return
    image_paths = res_img["result"].get("image_paths", [])
    print(f"✅ 生成 {len(image_paths)} 张图片: {work_dir / 'images'}")

    # ==========================================
    # Step 2: 图片转视频 (调用 video_generator)
    # ==========================================
    log_step(2, 5, "图片合成视频")
    res_vid = skill_manager.run(
        "video_generator",
        image_dir=str(work_dir / "images"),
        output_path=str(work_dir / "video_raw.mp4"),
        fps=1, 
        duration_per_image=2.0
    )
    
    if res_vid.get("status") != "success":
        print(f"❌ 视频合成失败: {res_vid.get('error')}")
        return
    video_path = res_vid["result"].get("output_path")
    print(f"✅ 视频生成: {video_path}")

    # ==========================================
    # Step 3: 生成配乐 (调用 music_generator)
    # ==========================================
    log_step(3, 5, "AI 生成配乐")
    res_music = skill_manager.run(
        "music_generator",
        topic=topic,
        emotion=emotion,
        duration=15, 
        output_path=str(work_dir / "music.mp3")
    )
    
    if res_music.get("status") != "success":
        print(f"⚠️ 音乐生成失败 (跳过): {res_music.get('error')}")
        audio_path = None
    else:
        audio_path = res_music["result"].get("audio_file")
        print(f"✅ 音乐生成: {audio_path}")

    # ==========================================
    # Step 4: 音视频合并 (参考 add_music_to_video.py 逻辑)
    # ==========================================
    log_step(4, 5, "音视频合并")
    final_video = video_path
    if audio_path and Path(audio_path).exists():
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            final_video = work_dir / "final_video.mp4"
            cmd = [
                ffmpeg, "-y",
                "-i", str(video_path),
                "-stream_loop", "-1", "-i", str(audio_path),
                "-shortest",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                str(final_video)
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"✅ 最终视频: {final_video}")
        else:
            print("⚠️ 未找到 ffmpeg，跳过音频合并")
    else:
        print("⚠️ 无音乐，使用原视频")

    # ==========================================
    # Step 5: 自动发布 (调用 social_auto_upload)
    # ==========================================
    if do_publish:
        log_step(5, 5, "自动发布到社交平台")
        res_pub = skill_manager.run(
            "social_auto_upload",
            platform="tencent", 
            file=str(final_video),
            title=topic,
            desc=f"AI 自动生成视频：{topic}",
            tags=["AI", "ArtForge", topic]
        )
        if res_pub.get("status") == "success":
            print("✅ 发布成功！")
        else:
            print(f"❌ 发布失败: {res_pub.get('error')}")
    else:
        log_step(5, 5, "跳过发布")

    print(f"\n🎉 流水线执行完毕！总耗时: {time.time() - start_time:.1f}秒")
    print(f"📂 产物目录: {work_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True, help="视频/创作主题")
    parser.add_argument("--count", type=int, default=5, help="生成图片数量")
    parser.add_argument("--emotion", default="epic", help="音乐情绪 (epic/peaceful/joyful)")
    parser.add_argument("--publish", action="store_true", help="完成后自动发布")
    args = parser.parse_args()
    
    run_pipeline(args.topic, args.count, args.emotion, args.publish)