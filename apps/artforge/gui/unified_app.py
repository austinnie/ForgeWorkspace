# apps/artforge/gui/unified_app.py
"""
ArtForge Ultimate - 超级工作台 (修复版 - 像素魔法 API 路由 + Gradio 6.0 兼容)
1. 完整复用 app.py 的 ArtForgeApp 类
2. 通用生图 Tab (Agnes API / 本地 ControlNet)
3. 🪄 像素魔法 Tab (修复：API 模式下自动降级为 Prompt-based Img2Img)
4. 技能中心
"""
import gradio as gr
import sys
import os
import json
import logging
import tempfile
from pathlib import Path
from PIL import Image
from datetime import datetime

# ==========================================
# 1. 路径注入 & 环境初始化
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH, override=True)
    except ImportError:
        pass

# ==========================================
# 2. 导入核心模块
# ==========================================
try:
    from forgecore.skills.manager import SkillManager, skill_manager
    from forgecore.config.registry import ModelRegistry
    from forgecore.engines import create_engine
    print("✅ ForgeCore 基盘加载成功")
except ImportError as e:
    print(f"❌ ForgeCore 加载失败: {e}")
    sys.exit(1)

try:
    from apps.artforge.gui.app import ArtForgeApp
    print("✅ ArtForgeApp (app.py) 导入成功")
except ImportError as e:
    print(f"⚠️ app.py 导入失败: {e}")
    ArtForgeApp = None

skill_manager.scan()

# ==========================================
# 3. 核心辅助函数：自动保存图片
# ==========================================
def _save_image_automatically(image: Image.Image, prefix: str = "artforge") -> str:
    if image is None: return ""
    try:
        save_dir = PROJECT_ROOT / "output"
        try:
            from forgecore.config.paths import Paths
            save_dir = Paths.OUTPUT_DIR
        except: pass
        save_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = save_dir / f"{prefix}_{timestamp}.png"
        if image.mode not in ('RGB', 'RGBA'): image = image.convert('RGB')
        image.save(save_path)
        return str(save_path)
    except Exception as e:
        print(f"⚠️ 自动保存图片失败: {e}")
        return ""

# ==========================================
# 4. Tab 1: 东方艺术
# ==========================================
def build_art_forge_tab(app_instance: ArtForgeApp):
    with gr.Tab("🎨 东方艺术"):
        if app_instance: app_instance._build_generation_tab()
        else: gr.Markdown(" app.py 未找到")

# ==========================================
# 5. Tab 2: 通用生图 & ControlNet
# ==========================================
def build_general_gen_tab():
    with gr.Tab("🧍 通用生图 & ControlNet"):
        gr.Markdown("### 🧍 图生图 / ControlNet 工作台")
        with gr.Row():
            with gr.Column(scale=1):
                ref_image = gr.Image(label="📎 上传参考图", type="pil", height=300)
                engine_mode = gr.Radio(choices=[("☁️ Agnes API", "agnes"), ("💻 本地模型", "local")], value="agnes", label="生成引擎")
                local_model_dd = gr.Dropdown(choices=[m["name"] for m in ModelRegistry.scan_checkpoints("sd15")], label="本地模型", value=None)
                gen_prompt = gr.Textbox(label="提示词", value="masterpiece, best quality", lines=2)
                gen_neg = gr.Textbox(label="负面提示词", value="worst quality", lines=1)
                with gr.Group():
                    cn_type_dd = gr.Dropdown(choices=["openpose", "canny", "depth", "lineart", "无 (纯图生图)"], label="ControlNet 类型", value="无 (纯图生图)")
                    cn_strength = gr.Slider(0.1, 1.0, value=0.6, label="强度")
                gen_btn = gr.Button("🚀 生成", variant="primary", size="lg")
            with gr.Column(scale=1):
                gen_out = gr.Image(label="结果", type="pil", height=400)
                gen_log = gr.Textbox(label="日志", lines=10)

        def run_img2img(ref_img, mode, model_name, prompt, negative, cn_type, strength):
            logs = ["🚀 启动..."]
            if ref_img is None: return None, " 必须上传参考图！"
            try:
                final_image = None
                if mode == "agnes":
                    logs.append("☁️ Agnes API 图生图")
                    from gui.common import load_env_config
                    engine = create_engine("agnes", load_env_config())
                    try:
                        final_image = engine.image_to_image(prompt=prompt, image=ref_img, strength=strength, width=768, height=1024)
                    except TypeError:
                        final_image = engine.image_to_image(prompt=prompt, images=[ref_img], strength=strength)
                    logs.append("✅ 完成")
                else:
                    if not model_name: return None, "❌ 请选择模型"
                    model_obj = next((m for m in ModelRegistry.scan_checkpoints("sd15") if m["name"] == model_name), None)
                    if not model_obj: return None, "❌ 找不到模型"
                    res = skill_manager.run("controlnet", action="generate", image=ref_img, prompt=prompt, negative_prompt=negative, model_path=model_obj["absolute_path"], controlnet_type=cn_type if cn_type != "无 (纯图生图)" else "canny", controlnet_conditioning_scale=strength if cn_type != "无 (纯图生图)" else 0.0)
                    if res.get("status") == "success":
                        out = res["result"].get("output_path")
                        if out and Path(out).exists(): final_image = Image.open(out)
                        elif "image" in res["result"]: final_image = res["result"]["image"]
                
                if final_image:
                    save_path = _save_image_automatically(final_image, prefix="img2img")
                    if save_path: logs.append(f"💾 已保存: {save_path}")
                    return final_image, "\n".join(logs)
                return None, "\n".join(logs)
            except Exception as e: return None, f"❌ 错误: {e}"

        gen_btn.click(fn=run_img2img, inputs=[ref_image, engine_mode, local_model_dd, gen_prompt, gen_neg, cn_type_dd, cn_strength], outputs=[gen_out, gen_log])

# ==========================================
# 6.  Tab 3: 像素魔法 (修复 API 路由)
# ==========================================
def build_pixel_magic_tab():
    with gr.Tab("🪄 像素魔法 (Pixel Magic)"):
        gr.Markdown("### 🪄 一键像素编辑 (Add Glasses / Tattoo / etc.)")
        gr.Markdown("💡 **逻辑**：上传参考图 -> 选择技能 -> 自动保存。**无需提示词**.")
        
        # ✅ 所有像素编辑类技能（按功能分类）
        PIXEL_SKILLS = [
            # ===== 配饰/装饰添加 =====
            "add_glasses",        # 添加眼镜
            "add_tattoo",         # 添加纹身
            "add_animal_ears",    # 添加动物耳朵
            "add_background_objects",  # 添加背景物体
            "add_glasses",        # 添加眼镜（重复，保留一个）
            
            # ===== 人物特征修改 =====
            "change_hair",        # 改变发型
            "change_age",         # 改变年龄
            "change_gender",      # 改变性别
            "change_body_type",   # 改变体型
            "change_expression",  # 改变表情
            "change_eye_color",   # 改变眼睛颜色
            "change_makeup",      # 改变妆容
            "change_skin_tone",   # 改变肤色
            "change_nationality", # 改变国籍/种族
            "change_face",        # 改变面部特征
            
            # ===== 服装修改 =====
            "change_clothes",     # 改变服装
            "change_clothing_style",  # 改变服装风格
            "remove_clothes",     # 移除服装
            
            # ===== 姿态/视角修改 =====
            "change_pose",        # 改变姿态
            "change_perspective", # 改变视角
            "expand_to_full_body", # 扩展到全身
            
            # ===== 环境/背景修改 =====
            "change_background",  # 改变背景
            "change_furniture",   # 改变家具
            "change_lighting",    # 改变光照
            "day_night_transfer", # 白天/夜晚转换
            "season_transfer",    # 季节转换
            "weather_transfer",   # 天气转换
            
            # ===== 物体编辑 =====
            "remove_object",      # 移除物体
            "replace_object",     # 替换物体
            
            # ===== 风格转换 =====
            "anime_to_real",      # 动漫转真实
            "real_to_anime",      # 真实转动漫
            "style_transfer",     # 风格迁移
            "sketch_to_real",     # 素描转真实
            "colorize_sketch",    # 素描上色
            "photo_realistic",    # 照片写实
            
            # ===== 特殊效果 =====
            "fix_human_anatomy",  # 修复人体结构
            "mosaic_reducer",     # 减少马赛克
            "old_photo_restore",  # 老照片修复
            "photo_restorer",     # 照片修复
            "human_to_robot",     # 人类转机器人
            "fantasy_character",  # 幻想角色
            "mecha_generator",    # 机甲生成
            
            # ===== 场景预设 =====
            "intimate_closeup",   # 亲密特写
            "bathroom_nude",      # 浴室场景
            "beach_lingerie",     # 海滩泳装
            "bedroom_lingerie",   # 卧室场景
            "bedroom_nude",       # 卧室场景
            "pool_nude",          # 泳池场景
            "studio_nude",        # 影棚场景
            "nude_oil_painting",  # 裸体油画
            "nude_sculpture",     # 裸体雕塑
        ]
        
        with gr.Row():
            with gr.Column(scale=1):
                magic_skill_dd = gr.Dropdown(
                    choices=PIXEL_SKILLS, 
                    value="add_glasses", 
                    label="✨ 选择魔法技能"
                )
                magic_ref_image = gr.Image(label="📎 上传参考图 (必须)", type="pil", height=300)
                # ✅ 修复：默认改为本地模型，因为 add_glasses 等技能原生只支持本地
                magic_engine_mode = gr.Radio(
                    choices=[("☁️ Agnes API (模拟)", "agnes"), ("💻 本地模型 (推荐)", "local")], 
                    value="local", 
                    label="生成引擎"
                )
                magic_local_model_dd = gr.Dropdown(
                    choices=[m["name"] for m in ModelRegistry.scan_checkpoints("sd15")], 
                    label="本地模型", 
                    value=None
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
                
                # ✅ 核心修复：API 模式下的智能路由
                if mode == "agnes":
                    logs.append(f"☁️ 使用 Agnes API 模拟 {skill_name}...")
                    logs.append("⚠️ 注意：当前技能不支持原生 API，已自动切换为 Prompt-based Img2Img")
                    
                    # 构建模拟提示词（扩展版）
                    prompt_map = {
                        # 配饰类
                        "add_glasses": "wearing elegant glasses, sophisticated, masterpiece",
                        "add_tattoo": "with beautiful tattoo on skin, artistic, masterpiece",
                        "add_animal_ears": "with cute animal ears, fox ears, cat ears, masterpiece",
                        "add_background_objects": "with detailed background objects, rich environment, masterpiece",
                        
                        # 人物特征类
                        "change_hair": "different hairstyle, detailed hair, masterpiece",
                        "change_age": "different age, younger/older, masterpiece",
                        "change_gender": "gender swap, masterpiece",
                        "change_body_type": "different body type, masterpiece",
                        "change_expression": "different facial expression, masterpiece",
                        "change_eye_color": "different eye color, detailed eyes, masterpiece",
                        "change_makeup": "different makeup style, masterpiece",
                        "change_skin_tone": "different skin tone, masterpiece",
                        "change_nationality": "different ethnicity, masterpiece",
                        "change_face": "different facial features, masterpiece",
                        
                        # 服装类
                        "change_clothes": "wearing different clothes, masterpiece",
                        "change_clothing_style": "different clothing style, masterpiece",
                        "remove_clothes": "without clothes, masterpiece",
                        
                        # 姿态/视角类
                        "change_pose": "different pose, masterpiece",
                        "change_perspective": "different perspective angle, masterpiece",
                        "expand_to_full_body": "full body view, masterpiece",
                        
                        # 环境类
                        "change_background": "beautiful new background, scenic, masterpiece",
                        "change_furniture": "different furniture, masterpiece",
                        "change_lighting": "different lighting, dramatic lighting, masterpiece",
                        "day_night_transfer": "night time, moonlight, masterpiece",
                        "season_transfer": "different season, masterpiece",
                        "weather_transfer": "different weather, rain, snow, masterpiece",
                        
                        # 物体编辑
                        "remove_object": "clean background, no objects, masterpiece",
                        "replace_object": "replaced object, masterpiece",
                        
                        # 风格转换
                        "anime_to_real": "photorealistic, real photo, masterpiece",
                        "real_to_anime": "anime style, anime illustration, masterpiece",
                        "style_transfer": "artistic style transfer, masterpiece",
                        "sketch_to_real": "photorealistic, detailed, masterpiece",
                        "colorize_sketch": "colorized, vibrant colors, masterpiece",
                        "photo_realistic": "photorealistic, hyperrealistic, masterpiece",
                        
                        # 特殊效果
                        "fix_human_anatomy": "correct anatomy, perfect proportions, masterpiece",
                        "mosaic_reducer": "high quality, clear details, masterpiece",
                        "old_photo_restore": "restored, high quality, masterpiece",
                        "photo_restorer": "restored photo, high quality, masterpiece",
                        "human_to_robot": "cyborg, robot, mechanical parts, masterpiece",
                        "fantasy_character": "fantasy character, magical, masterpiece",
                        "mecha_generator": "mecha, robot suit, mechanical, masterpiece",
                        
                        # 场景预设
                        "intimate_closeup": "intimate closeup, detailed face, masterpiece",
                        "bathroom_nude": "in bathroom, steam, masterpiece",
                        "beach_lingerie": "on beach, summer, masterpiece",
                        "bedroom_lingerie": "in bedroom, cozy, masterpiece",
                        "bedroom_nude": "in bedroom, intimate, masterpiece",
                        "pool_nude": "by pool, water, masterpiece",
                        "studio_nude": "in studio, professional lighting, masterpiece",
                        "nude_oil_painting": "oil painting style, classical art, masterpiece",
                        "nude_sculpture": "sculpture style, marble, masterpiece",
                    }
                    
                    sim_prompt = prompt_map.get(skill_name, f"{skill_name.replace('_', ' ')}, masterpiece")
                    
                    from gui.common import load_env_config
                    engine = create_engine("agnes", load_env_config())
                    try:
                        final_image = engine.image_to_image(
                            prompt=sim_prompt, 
                            image=ref_img, 
                            strength=0.6, 
                            width=768, 
                            height=1024
                        )
                    except TypeError:
                        final_image = engine.image_to_image(
                            prompt=sim_prompt, 
                            images=[ref_img], 
                            strength=0.6
                        )
                    logs.append("✅ Agnes API 模拟执行成功")

                # 本地模式：走原有 skill 流程
                else:
                    if not model_name: 
                        return None, "❌ 请选择本地模型"
                    model_obj = next((m for m in ModelRegistry.scan_checkpoints("sd15") if m["name"] == model_name), None)
                    if not model_obj: 
                        return None, "❌ 找不到模型"
                    
                    # 将 PIL Image 保存为临时文件
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        ref_img.save(tmp.name)
                        temp_img_path = tmp.name
                    logs.append(f"📂 图片暂存: {Path(temp_img_path).name}")

                    output_path = temp_img_path.replace(".png", f"_{skill_name}_out.png")
                    kwargs = {
                        "image_path": temp_img_path, 
                        "output_path": output_path, 
                        "model_path": model_obj["absolute_path"]
                    }
                    
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
                        logs.append(f" 本地技能失败: {res.get('error')}")
                        # 降级尝试
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

                    try: 
                        os.remove(temp_img_path)
                    except: 
                        pass

                # 自动保存
                if final_image:
                    save_path = _save_image_automatically(final_image, prefix=f"magic_{skill_name}")
                    if save_path: 
                        logs.append(f"💾 已保存: {save_path}")
                    return final_image, "\n".join(logs)
                
                return None, "\n".join(logs) + "\n❌ 未能生成图片"
            except Exception as e:
                return None, f"❌ 错误: {e}"

        magic_btn.click(
            fn=run_pixel_magic, 
            inputs=[magic_skill_dd, magic_ref_image, magic_engine_mode, magic_local_model_dd], 
            outputs=[magic_out, magic_log]
        )
        
# ==========================================
# 7. Tab 4: 技能中心
# ==========================================
def build_skill_hub_tab():
    with gr.Tab("🛠️ 技能中心"):
        skill_names = [s['name'] for s in skill_manager.list_skills()]
        with gr.Row():
            with gr.Column(scale=1):
                skill_dd = gr.Dropdown(choices=skill_names, label="技能", value="search_engine" if "search_engine" in skill_names else skill_names[0])
                params_input = gr.Textbox(label="参数 (JSON)", value='{"query": "AI"}', lines=4)
                run_btn = gr.Button("🚀 执行", variant="primary")
            with gr.Column(scale=1):
                log_output = gr.Textbox(label="日志", lines=10)
                result_output = gr.JSON(label="结果")
        def execute_skill(name, json_str):
            try:
                kwargs = json.loads(json_str) if json_str.strip() else {}
                res = skill_manager.run(name, **kwargs)
                return f"状态: {res.get('status')}", res
            except Exception as e: return f"❌ {e}", {}
        run_btn.click(fn=execute_skill, inputs=[skill_dd, params_input], outputs=[log_output, result_output])

# ==========================================
# 8. 主 GUI (修复 Gradio 6.0 警告)
# ==========================================
def build_unified_gui():
    app = ArtForgeApp() if ArtForgeApp else None
    # ✅ 修复：theme 参数移到 launch() 中
    with gr.Blocks(title="ArtForge Ultimate") as demo:
        with gr.Row():
            gr.Markdown("#  ArtForge Ultimate")
            gr.Markdown(f"**状态**: 🟢 就绪 | **技能**: {len(skill_manager.list_skills())} 个")
        with gr.Tabs():
            build_art_forge_tab(app)
            build_general_gen_tab()
            build_pixel_magic_tab()
            build_skill_hub_tab()
    return demo

if __name__ == "__main__":
    demo = build_unified_gui()
    # ✅ 修复：theme 在这里传入
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, inbrowser=True, theme=gr.themes.Soft())