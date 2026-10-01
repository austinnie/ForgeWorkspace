# apps/artforge/main.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ArtForge - 东方艺术生成工坊 (Monorepo 联调版)"""
import sys
from pathlib import Path

# 🔥 1. 注入 ForgeCore 路径
CORE_PATH = Path(__file__).resolve().parent.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

print("=" * 50)
print("🎨 ArtForge 联调测试")
print("=" * 50)

# 🔥 2. 测试导入 ForgeCore
try:
    import forgecore
    print(f"✅ ForgeCore 版本: {forgecore.__version__}")
    print(f"   .env 来源: {forgecore._env_source}")
except Exception as e:
    print(f"❌ ForgeCore 导入失败: {e}")
    sys.exit(1)

# 🔥 3. 测试引擎创建
try:
    from forgecore.engines import create_engine
    
    # 测试 Pollinations（免费，无需 Key）
    print("\n🚀 测试 Pollinations 引擎...")
    engine = create_engine("pollinations")
    print(f"   ✅ 引擎创建成功: {type(engine).__name__}")
    
    # 测试 Agnes（需要 Key，仅测试创建不测试生图）
    print("\n🚀 测试 Agnes 引擎...")
    try:
        agnes = create_engine("agnes")
        print(f"   ✅ 引擎创建成功: {type(agnes).__name__}")
    except Exception as e:
        print(f"   ⚠️ Agnes 创建异常 (可能缺少 Key): {e}")
        
except Exception as e:
    print(f"❌ 引擎测试失败: {e}")
    import traceback
    traceback.print_exc()

# 🔥 4. 测试提示词构建
try:
    from forgecore.prompt import PromptBuilder, PromptComposer
    print("\n📝 测试提示词模块...")
    if PromptBuilder:
        print(f"   ✅ PromptBuilder 可用 (ArtForge)")
    if PromptComposer:
        print(f"   ✅ PromptComposer 可用 (LayerForge)")
except Exception as e:
    print(f"   ⚠️ 提示词模块异常: {e}")

print("\n" + "=" * 50)
print("✅ Monorepo 联调测试完成！")
print("=" * 50)