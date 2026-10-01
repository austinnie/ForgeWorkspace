#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""LayerForge - 6层结构化生图"""
import sys
from pathlib import Path

CORE_PATH = Path(__file__).parent.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

print("🏗️ LayerForge 启动，已加载 ForgeCore...")
