# test_skills.py (放在 ForgeWorkspace 根目录)
import sys
from pathlib import Path

# 1. 注入根目录
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

try:
    from forgecore.skills.manager import SkillManager
    
    mgr = SkillManager()
    count = mgr.scan()
    print(f"\n✅ 扫描完成！共发现 {count} 个技能。\n")
    
    # 列出前 5 个
    for s in mgr.list_skills()[:5]:
        print(f" - {s['name']} (v{s['version']})")
        
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保 forgecore/skills/ 下有 manager.py 和 base.py")
except Exception as e:
    print(f"❌ 运行错误: {e}")