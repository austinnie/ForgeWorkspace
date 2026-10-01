# scripts/create_junctions.py
"""使用 Windows 目录联接 (Junction) 彻底解决旧代码相对路径问题"""
import os
import subprocess
import sys

def create_junction(link_path, target_path):
    link_path = os.path.abspath(link_path)
    target_path = os.path.abspath(target_path)
    
    # 1. 如果目标位置已经存在（且不是联接），先清理它
    if os.path.exists(link_path):
        if os.path.islink(link_path) or os.path.isdir(link_path):
            try:
                # Junction 可以用 rmdir 删除，普通目录如果为空也可以
                os.rmdir(link_path) 
                print(f"  🧹 已清理旧的联接/空目录: {link_path}")
            except OSError:
                print(f"  ️ {link_path} 不为空或无法删除，请手动删除该文件夹后重试。")
                return False

    # 2. 创建 Directory Junction
    # mklink /J 创建目录联接
    cmd = f'mklink /J "{link_path}" "{target_path}"'
    print(f"  🔗 执行: {cmd}")
    
    # 使用 shell=True 以便 cmd 能识别 mklink
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='gbk')
    
    if result.returncode == 0 or "已创建" in result.stdout or "created" in result.stdout.lower():
        print(f"  ✅ 成功创建联接！")
        return True
    else:
        print(f"  ❌ 创建失败！")
        print(f"     错误信息: {result.stdout.strip()}")
        print(f"     提示: 如果提示'权限不足'，请以【管理员身份】运行此脚本。")
        return False

print("=" * 60)
print("🚀 正在创建目录联接 (Junction) 以解决路径问题...")
print("=" * 60)

REAL_MODELS = r"E:\SD_OpenVINO\models"
WORKSPACE = r"E:\SD_OpenVINO\ForgeWorkspace"

# 联接 1: 在 ForgeWorkspace 根目录下创建 models 联接
print("\n1. 在 ForgeWorkspace 根目录创建联接...")
create_junction(
    os.path.join(WORKSPACE, "models"), 
    REAL_MODELS
)

# 联接 2: 在 sd_gui 目录下创建 models 联接
print("\n2. 在 apps/sd_gui 目录下创建联接...")
create_junction(
    os.path.join(WORKSPACE, "apps", "sd_gui", "models"), 
    REAL_MODELS
)

print("\n" + "=" * 60)
print("💡 现在，无论旧代码怎么拼接相对路径，")
print("   只要它访问 ForgeWorkspace/models 或 sd_gui/models，")
print("   Windows 都会自动把它重定向到 E:\\SD_OpenVINO\\models！")
print("=" * 60)
print("\n👉 请关闭当前运行的 GUI，然后重新运行: python apps/sd_gui/main.py")