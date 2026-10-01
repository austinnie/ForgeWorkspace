# scripts/clean_all_injections.py
"""清理所有文件中的错误注入代码，确保字体加载逻辑干净正确"""
import re
from pathlib import Path

WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")

# 需要清理的文件列表
files_to_clean = [
    WORKSPACE / "apps" / "artforge" / "compose_artwork.py",
    WORKSPACE / "apps" / "artforge" / "services" / "inscription_generator.py",
    WORKSPACE / "apps" / "artforge" / "services" / "seal_generator.py",
]

print("=" * 70)
print("🧹 正在清理所有文件中的错误注入代码...")
print("=" * 70 + "\n")

# 匹配错误注入的正则模式 (从 "# 🔥 [AUTO-INJECTED]" 到 "return None")
injection_pattern = re.compile(r"#\s*🔥\s*\[AUTO-INJECTED\].*?return\s+None\s*#\s*将使用 PIL 默认字体\n+", re.DOTALL)

cleaned_count = 0
for py_file in files_to_clean:
    if not py_file.exists():
        continue
        
    content = py_file.read_text(encoding="utf-8")
    
    if injection_pattern.search(content):
        # 移除注入的代码
        clean_content = injection_pattern.sub("", content)
        
        # 额外清理：如果文件里有 _get_zhuan_seal_font 的调用，也替换掉
        # 例如：_get_zhuan_seal_font(...) -> None (或者直接删除这行调用，取决于上下文)
        # 这里我们简单地将 _get_zhuan_seal_font(...) 替换为 None，让代码 fallback 到默认逻辑
        clean_content = re.sub(r'_get_zhuan_seal_font\([^)]*\)', 'None', clean_content)
        
        py_file.write_text(clean_content, encoding="utf-8")
        print(f"✅ 已清理: {py_file.relative_to(WORKSPACE)}")
        cleaned_count += 1
    else:
        print(f"ℹ️ 无需清理: {py_file.relative_to(WORKSPACE)}")

print("\n" + "=" * 70)
if cleaned_count > 0:
    print(f"🎉 成功清理了 {cleaned_count} 个文件中的垃圾注入代码！")
    print("\n💡 字体加载说明:")
    print("   现在代码将依赖 compose_artwork.py 中的 FONT_CANDIDATES 列表。")
    print("   请确保 Mini_zhuan.ttf 已正确放置在 shared_assets/fonts/ 目录下。")
else:
    print("所有文件已经是干净的，无需清理。")

print("\n👉 请重启 ArtForge 并再次测试生成。")
print("=" * 70)