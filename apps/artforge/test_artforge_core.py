# apps/artforge/test_artforge_core.py
import sys
from pathlib import Path

# 🔥 核心修复：将项目根目录 (ForgeWorkspace) 加入 sys.path，而不是 forgecore 目录
APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent.parent  # 指向 E:\SD_OpenVINO\ForgeWorkspace

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 60)
print("🧪 ArtForge & ForgeCore 核心集成测试")
print("=" * 60)

# 2. 测试 ForgeCore 配置模块导入
print("\n [1/4] 测试 ForgeCore 配置模块...")
try:
    from forgecore.config.paths import Paths
    from forgecore.config.registry import ModelRegistry
    from forgecore.config.settings import settings
    
    print("✅ 模块导入成功！")
    print(f"   📂 模型基目录 (绝对路径): {Paths.BASE_MODELS_DIR}")
    print(f"   📂 项目输出目录: {Paths.OUTPUT_DIR}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    print("💡 提示: 请检查 sys.path 是否包含了项目根目录。")
    sys.exit(1)

# 3. 测试本地模型扫描能力
print("\n [2/4] 扫描本地模型仓库...")
try:
    sd15_models = ModelRegistry.scan_checkpoints("sd15")
    sdxl_models = ModelRegistry.scan_checkpoints("sdxl")
    sd15_loras = ModelRegistry.scan_loras("sd15")
    
    print(f"   ✅ 发现 SD1.5 主模型: {len(sd15_models)} 个")
    if sd15_models: print(f"      └─ 示例: {sd15_models[0]['name']} ({sd15_models[0]['size_mb']}MB)")
        
    print(f"   ✅ 发现 SDXL 主模型: {len(sdxl_models)} 个")
    if sdxl_models: print(f"      └─ 示例: {sdxl_models[0]['name']} ({sdxl_models[0]['size_mb']}MB)")
        
    print(f"   ✅ 发现 SD1.5 LoRA: {len(sd15_loras)} 个")
except Exception as e:
    print(f"   ⚠️ 扫描出错 (可能是目录不存在，不影响后续): {e}")

# 4. 测试 Settings 配置管理器
print("\n🔍 [3/4] 测试 Settings 配置管理器...")
try:
    default_model = settings.get_default_model_path("sd15")
    print(f"   ✅ 获取默认 SD1.5 模型路径: {default_model or '未配置/未找到'}")
except Exception as e:
    print(f"   ⚠️ Settings 测试出错: {e}")

# 5. 测试 Gradio UI 构建
print("\n [4/4] 测试 Gradio UI 界面构建...")
try:
    import gui.app as artforge_gui
    if hasattr(artforge_gui, 'build_ui'):
        demo = artforge_gui.build_ui()
        print("✅ Gradio UI 构建成功！界面骨架已就绪。")
    else:
        print("⚠️ 未找到 build_ui() 函数，请检查 gui/app.py")
except Exception as e:
    print(f"❌ UI 构建失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🎉 测试完成！如果上面没有红色报错，说明重构完美成功。")
print("=" * 60)