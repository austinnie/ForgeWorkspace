#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PromptForge - Monorepo 启动器"""
import sys
import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

CORE_PATH = APP_ROOT.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

for extra in ["core", "config", "skills"]:
    p = APP_ROOT / extra
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

ENV_PATH = APP_ROOT.parent.parent / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except ImportError:
        pass

print("=" * 60)
print("🚀 正在启动: PromptForge")
print("=" * 60)
print("✅ PromptForge 环境就绪，请使用 CLI 或 FastAPI 启动。")
