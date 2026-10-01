# scripts/create_models_junction.py
"""使用 Windows 目录联接 (Junction) 彻底解决旧代码相对路径问题"""
import os
import subprocess
from pathlib import Path

WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")
SD_GUI_DIR = WORKSPACE / "apps" / "sd_gui"
REAL_MODELS = Path(r"E:\SD_OpenVINO\models")

# 目标联接路径：在 sd_gui 目录下创建一个名为 models 的联接点
JUNCTION_PATH = SD_GUI_DIR / "models"

print("=" * 60)
print("🚀 正在创建目录联接 (Junction) 以解决路径问题...")
print("=" * 60)

# 1. 如果已经存在（且不是联接），先删除它
if JUNCTION_PATH.exists():
    if JUNCTION_PATH.is_symlink() or JUNCTION_PATH.is_dir():
        print(f"⚠️ 发现已存在的 models 目录/链接，正在清理...")
        # 注意：如果是普通目录且有文件，rmtree 会删除真实文件！
        # 所以我们先检查它是否是 Junction
        try:
            # 尝试作为 symlink 删除
            JUNCTION_PATH.unlink()
            print("✅ 已删除旧的符号链接")
        except PermissionError:
            # 如果是 Junction，可能需要用 rmdir
            os.rmdir(JUNCTION_PATH)
            print("✅ 已删除旧的目录联接")
        except Exception as e:
            print(f"❌ 清理失败: {e}")
            print("💡 请手动删除 E:\\SD_OpenVINO\\ForgeWorkspace\\apps\\sd_gui\\models 文件夹后重试")
            exit(1)

# 2. 创建 Directory Junction
# mklink /J 创建目录联接，不需要管理员权限（在 Windows 10/11 开发者模式下）
cmd = ['cmd', '/c', 'mklink', '/J', str(JUNCTION_PATH), str(REAL_MODELS)]

print(f"\n🔗 正在执行: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk')

if result.returncode == 0:
    print("✅ 目录联接创建成功！")
    print(f"   虚拟路径: {JUNCTION_PATH}")
    print(f"   真实指向: {REAL_MODELS}")
    print("\n💡 现在，无论旧代码怎么拼接相对路径，只要它访问 sd_gui/models，")
    print("   Windows 都会自动把它重定向到 E:\\SD_OpenVINO\\models！")
else:
    print("❌ 创建失败！")
    print(f"   错误信息: {result.stderr}")
    print("\n💡 可能原因：")
    print("   1. 您的 Windows 未开启'开发者模式'。")
    print("   2. 请以管理员身份运行此脚本。")
    print("   3. 或者，您可以手动以管理员身份打开 CMD，运行：")
    print(f'      mklink /J "{JUNCTION_PATH}" "{REAL_MODELS}"')

print("\n" + "=" * 60)
print("👉 请关闭当前运行的 GUI，然后重新运行: python apps/sd_gui/main.py")
print("=" * 60)