#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SD Generator CLI (终极修复完整版)
1. 彻底屏蔽 controlnet_aux / timm / SegDetector 的所有烦人警告
2. 修复变量名不匹配导致的 NameError
3. 完美支持三层预设目录结构
4. 支持模型自动兜底
"""
import sys
import os
import argparse
import random
import importlib.util
import warnings
import logging
import builtins
from pathlib import Path
from datetime import datetime

# ==========================================
# 0. 全局静音设置 (必须在所有 import 之前！)
# ==========================================
# 1. 屏蔽 Python 标准的 FutureWarning 和 UserWarning
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# 2. 屏蔽第三方库的日志输出
logging.getLogger("controlnet_aux").setLevel(logging.CRITICAL)
logging.getLogger("timm").setLevel(logging.CRITICAL)
logging.getLogger("diffusers").setLevel(logging.CRITICAL)

# 3. 彻底拦截包含 "SegDetector" 或 "UniformerDetector" 的 print 输出
_original_print = builtins.print
def _safe_print(*args, **kwargs):
    msg = " ".join(str(a) for a in args)
    if "SegDetector" in msg or "UniformerDetector" in msg:
        return  # 直接丢弃，不打印
    _original_print(*args, **kwargs)
builtins.print = _safe_print

# ==========================================
# 1. 路径注入 & 加载 .env
# ==========================================
APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH, override=True)
    except ImportError:
        pass

# ==========================================
# 2. 导入 ForgeCore 基盘
# ==========================================
try:
    from forgecore.config.registry import ModelRegistry
    from forgecore.engines.local_engine import DiffusersEngine
    from forgecore.engines import create_engine
    from forgecore.prompt.composer import PromptComposer
    FORGE_CORE_AVAILABLE = True
except Exception as e:
    print(f"❌ ForgeCore 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==========================================
# 3. 预设系统 (完美支持三层目录结构)
# ==========================================
PRESETS_BASE = PROJECT_ROOT / "shared_assets" / "presets_by_app"

def scan_all_presets() -> dict:
    """
    扫描三层目录结构：
    presets_by_app/
      └── oriental_forge/       (第一层：App分类)
            └── region/         (第二层：主题分类)
                  └── dragon.py (第三层：预设文件)
    """
    result = {}
    if not PRESETS_BASE.exists():
        return result
        
    for app_dir in sorted(PRESETS_BASE.iterdir()):
        if not app_dir.is_dir() or app_dir.name.startswith('_'):
            continue
            
        app_presets = {}
        for theme_dir in sorted(app_dir.iterdir()):
            if not theme_dir.is_dir() or theme_dir.name.startswith('_'):
                continue
                
            py_files = sorted([
                f.stem for f in theme_dir.glob("*.py")
                if not f.stem.startswith('_') and f.stem != '__init__'
            ])
            
            if py_files:
                app_presets[theme_dir.name] = py_files
                
        if app_presets:
            result[app_dir.name] = app_presets
            
    return result

def load_preset_layers(app_name: str, theme_name: str, preset_name: str) -> dict:
    """加载指定三层路径下的预设 layers"""
    target = PRESETS_BASE / app_name / theme_name / f"{preset_name}.py"
    
    # 如果路径不对，尝试全局模糊搜索
    if not target.exists():
        for app_dir in PRESETS_BASE.iterdir():
            if app_dir.is_dir():
                for theme_dir in app_dir.iterdir():
                    if theme_dir.is_dir():
                        for f in theme_dir.glob(f"{preset_name}.py"):
                            target = f
                            break
                    if target.exists():
                        break
            if target.exists():
                break

    if not target.exists():
        return {}
        
    try:
        spec = importlib.util.spec_from_file_location(f"preset_{preset_name}", target)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, 'LAYERS'):
            return module.LAYERS
        elif hasattr(module, 'PRESET') and isinstance(module.PRESET, dict):
            return module.PRESET.get('layers', {})
    except Exception as e:
        print(f"⚠️ 加载预设 {preset_name} 失败: {e}")
    return {}

# ==========================================
# 4. 查询命令 (--list-*)
# ==========================================
def cmd_list_presets(args):
    print("\n" + "=" * 70)
    print("📚 预设库 (shared_assets/presets_by_app/)")
    print("=" * 70)
    presets = scan_all_presets()
    if not presets:
        print("⚠️ 未找到任何预设。")
        return
        
    total_apps = len(presets)
    total_themes = 0
    total_files = 0
    
    for app, themes in presets.items():
        print(f"\n📁 [{app}]")
        print("-" * 70)
        for theme, names in themes.items():
            print(f"  📂 {theme}/ ({len(names)} 个)")
            for i, name in enumerate(names, 1):
                print(f"    {name:<20}", end="")
                if i % 5 == 0:
                    print()
            if len(names) % 5 != 0:
                print()
            total_themes += 1
            total_files += len(names)
            
    print("\n" + "=" * 70)
    print(f" 统计: {total_apps} 个App分类, {total_themes} 个主题, {total_files} 个预设文件")
    print("=" * 70)
    print("\n💡 用法示例:")
    print("  python cli.py --app oriental_forge --theme region --preset dragon")

def cmd_list_models(args):
    print("\n" + "=" * 70)
    print("💻 本地模型库")
    print("=" * 70)
    for m_type in ["sd15", "sdxl"]:
        models = ModelRegistry.scan_checkpoints(m_type)
        print(f"\n📦 [{m_type.upper()}] (共 {len(models)} 个)")
        if not models:
            continue
        for i, m in enumerate(models[:5], 1):
            print(f"  {i}. {m['name']}")
        if len(models) > 5:
            print(f"  ... 还有 {len(models)-5} 个")

def cmd_list_apis(args):
    print("\n" + "=" * 70)
    print("☁️ 支持的 API 引擎")
    print("=" * 70)
    apis = ["freeapi", "pollinations", "agnes", "siliconflow", "tongyi", "yige", "hunyuan"]
    for i, api in enumerate(apis, 1):
        print(f"  {i}. {api}")

# ==========================================
# 5. 核心生成逻辑 (🔥 变量名已严格核对)
# ==========================================
def generate_image(
    app, theme, preset_name, prompt, negative, model_name, 
    steps, cfg, width, height, output_dir, use_api, api_provider, seed=None
):
    print("\n" + "=" * 70)
    print("🎨 SD Generator 启动")
    print("=" * 70)

    out_dir = Path(output_dir) if output_dir else APP_ROOT / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = out_dir / f"sd_gen_{timestamp}.png"

    # 1. 提示词处理
    layers = {}
    if preset_name:
        # 🔥 修复：这里使用函数参数 app 和 theme，不再报错
        layers = load_preset_layers(app or "", theme or "", preset_name)
        if not layers:
            print(f"⚠️ 未找到预设 '{preset_name}'，将使用自定义 prompt")
            
    if prompt:
        layers["subject"] = [prompt]
    if negative:
        layers["negative"] = [negative]

    composer = PromptComposer(layers=layers)
    final_prompt = composer.compose_random(max_tokens=75)
    final_negative = ", ".join(layers.get("negative", ["worst quality, low quality, blurry"]))

    print(f"✅ 提示词就绪: {final_prompt[:60]}...")

    # 2. 引擎调度
    image = None
    if seed is None:
        seed = random.randint(1, 2**32 - 1)

    if use_api:
        print(f"☁️ 正在使用 API 引擎: {api_provider}")
        config = {
            "AGNES_API_KEY": os.getenv("AGNES_API_KEY", ""),
            "AGNES_BASE_URL": os.getenv("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1"),
            "AGNES_IMAGE_MODEL": os.getenv("AGNES_IMAGE_MODEL", "agnes-image-2.1-flash"),
            "FREEAPI_MODEL": os.getenv("FREEAPI_MODEL", "grok-imagine-image-lite"),
            "POLLINATIONS_MODEL": os.getenv("POLLINATIONS_MODEL", "flux"),
        }
        engine = create_engine(api_provider, config=config)
        image = engine.generate_single(
            prompt=final_prompt, negative=final_negative,
            steps=steps, cfg=cfg, width=width, height=height, seed=seed
        )
    else:
        # 🔥 核心修复：如果用户没传 model_name，自动扫描并选择第一个 SD1.5 模型
        if not model_name:
            models = ModelRegistry.scan_checkpoints("sd15")
            if models:
                model_name = models[0]["name"]
                print(f"ℹ️ 未指定模型，自动选择默认: {model_name}")
            else:
                print("❌ 未找到本地模型！")
                print("💡 请先运行: python cli.py --list-models 查看可用模型")
                print("   或添加 --api 使用云端 API")
                return

        # 查找模型路径
        model_path = None
        model_type = "sd15"
        for m_type in ["sd15", "sdxl"]:
            models = ModelRegistry.scan_checkpoints(m_type)
            for m in models:
                if m["name"] == model_name:
                    model_path = m["absolute_path"]
                    model_type = m_type
                    break
            if model_path:
                break
                
        if not model_path:
            print(f"❌ 找不到模型: {model_name}")
            return

        # 分辨率自适应
        if model_type == "sdxl" and width == 512:
            width, height = 1024, 1024

        print(f"💻 本地模型: {model_path} ({model_type})")
        print(f"📐 分辨率: {width}x{height} | 步数: {steps} | CFG: {cfg}")
        
        engine = DiffusersEngine(model_type=model_type, device="CPU")
        print("⏳ 正在加载模型 (首次需 30-60 秒)...")
        engine.load_model(model_path)
        print("✅ 模型加载完成，开始生成...")
        
        image = engine.generate(
            prompt=final_prompt, negative_prompt=final_negative,
            width=width, height=height,
            num_inference_steps=steps, guidance_scale=cfg, seed=seed
        )

    # 3. 保存
    if image:
        image.save(save_path)
        print(f"\n✅ 生成成功！")
        print(f"📁 图片已保存: {save_path}")
    else:
        print("\n❌ 生成失败，未返回图片。")

# ==========================================
# 6. CLI 参数解析
# ==========================================
def main():
    parser = argparse.ArgumentParser(
        description="SD Generator CLI (基于 ForgeCore)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cli.py --list-presets              查看所有预设
  python cli.py --list-models               查看本地模型
  python cli.py --list-apis                 查看 API 引擎
  python cli.py --app oriental_forge --theme region --preset dragon
  python cli.py --preset dragon --api       自动搜索预设并用 API 生成
  python cli.py --prompt "a cat" --api      用 API 生成
  python cli.py --model aiiiiii01_v10 --prompt "a cat"
        """
    )

    # 查询命令
    parser.add_argument("--list-presets", action="store_true", help="列出所有预设分类和名称")
    parser.add_argument("--list-models",  action="store_true", help="列出本地可用模型")
    parser.add_argument("--list-apis",    action="store_true", help="列出支持的 API 引擎")

    # 预设相关
    parser.add_argument("--app",    type=str, default=None, help="App分类 (如 oriental_forge)")
    parser.add_argument("--theme",  type=str, default=None, help="主题分类 (如 region)")
    parser.add_argument("--preset", type=str, default=None, help="预设名称")

    # 提示词
    parser.add_argument("--prompt",   type=str, default=None, help="正向提示词")
    parser.add_argument("--negative", type=str, default=None, help="负面提示词")

    # 模型
    parser.add_argument("--model",        type=str, default=None, help="本地模型名称")
    parser.add_argument("--api",          action="store_true",    help="使用 API 引擎")
    parser.add_argument("--api-provider", type=str, default="freeapi", help="API 提供商")

    # 生成参数
    parser.add_argument("--steps",  type=int,   default=20,   help="采样步数 (默认 20)")
    parser.add_argument("--cfg",    type=float, default=7.5,  help="CFG Scale (默认 7.5)")
    parser.add_argument("--width",  type=int,   default=512,  help="宽度 (默认 512)")
    parser.add_argument("--height", type=int,   default=768,  help="高度 (默认 768)")
    parser.add_argument("--seed",   type=int,   default=None, help="随机种子")
    parser.add_argument("--output", type=str,   default=None, help="输出目录")

    args = parser.parse_args()

    # 处理查询命令
    if args.list_presets:
        cmd_list_presets(args)
        return
    if args.list_models:
        cmd_list_models(args)
        return
    if args.list_apis:
        cmd_list_apis(args)
        return

    # 检查是否提供了生成所需的参数
    if not args.prompt and not args.preset:
        parser.print_help()
        print("\n❌ 请提供 --prompt 或 --preset 参数")
        return

    # 执行生成 (🔥 参数名严格对齐 generate_image 的签名)
    generate_image(
        app=args.app,
        theme=args.theme,
        preset_name=args.preset,
        prompt=args.prompt,
        negative=args.negative,
        model_name=args.model,
        steps=args.steps,
        cfg=args.cfg,
        width=args.width,
        height=args.height,
        output_dir=args.output,
        use_api=args.api,
        api_provider=args.api_provider,
        seed=args.seed,
    )

if __name__ == "__main__":
    main()