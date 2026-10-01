# scripts/fix_compose_artwork_final.py
"""精准修复 compose_artwork.py：清理垃圾注入，强制使用 Mini_zhuan.ttf"""
import re
from pathlib import Path

FILE_PATH = Path(r"E:\SD_OpenVINO\ForgeWorkspace\apps\artforge\compose_artwork.py")

print("=" * 70)
print("🔧 正在精准修复 compose_artwork.py ...")
print("=" * 70 + "\n")

if not FILE_PATH.exists():
    print("❌ 找不到 compose_artwork.py")
    exit(1)

content = FILE_PATH.read_text(encoding="utf-8")

# 1. 彻底删除之前注入的垃圾函数 _get_zhuan_seal_font
# 匹配从 "# 🔥 [AUTO-INJECTED]" 到 "return None # 将使用 PIL 默认字体" 的所有内容
pattern_injection = re.compile(r"#\s*\s*\[AUTO-INJECTED\].*?return\s+None\s*#\s*将使用 PIL 默认字体\n", re.DOTALL)
if pattern_injection.search(content):
    content = pattern_injection.sub("", content)
    print("✅ 已清除之前注入的错误字体查找函数。")
else:
    print("ℹ️ 未找到之前的注入代码。")

# 2. 在 ARTIST_NAME 下方注入干净的字体常量
artist_pattern = re.compile(r'(ARTIST_NAME\s*=\s*["\'].*?["\'])')
if artist_pattern.search(content):
    font_constant = """

# 🎯 精准指定小篆字体路径 (相对路径，兼容 Monorepo 结构)
MINI_ZHUAN_FONT = Path(__file__).resolve().parent.parent / "shared_assets" / "fonts" / "Mini_zhuan.ttf"
"""
    content = artist_pattern.sub(r"\1" + font_constant, content)
    print("✅ 已注入 MINI_ZHUAN_FONT 常量。")

# 3. 修复 FONT_CANDIDATES 列表，将小篆字体放在首位
candidates_pattern = re.compile(r'FONT_CANDIDATES\s*=\s*\[(.*?)\]', re.DOTALL)
if candidates_pattern.search(content):
    new_candidates = """FONT_CANDIDATES = [
        MINI_ZHUAN_FONT,  # 第一优先级：强制使用小篆字体
        PROJECT_ROOT / "assets" / "fonts" / "calligraphy.ttf",
        PROJECT_ROOT / "assets" / "fonts" / "kai.ttf",
        Path("C:/Windows/Fonts/simkai.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]"""
    content = candidates_pattern.sub(new_candidates, content)
    print("✅ 已更新 FONT_CANDIDATES，小篆字体优先级最高。")

# 4. 修复 _load_font 方法中的错误调用
# 将 ImageFont.truetype(_get_zhuan_seal_font(str(self.font_path)), size) 
# 修复为 ImageFont.truetype(str(self.font_path), size)
load_font_pattern = re.compile(r'ImageFont\.truetype\(_get_zhuan_seal_font\(str\(self\.font_path\)\),\s*size\)')
if load_font_pattern.search(content):
    content = load_font_pattern.sub('ImageFont.truetype(str(self.font_path), size)', content)
    print("✅ 已修复 _load_font 方法中的错误调用。")

# 写回文件
FILE_PATH.write_text(content, encoding="utf-8")

print("\n" + "=" * 70)
print(" compose_artwork.py 修复完毕！")
print("💡 现在代码将直接、干净地加载 shared_assets/fonts/Mini_zhuan.ttf")
print("👉 请重启 ArtForge 并再次测试生成（勾选『题词』）。")
print("=" * 70)