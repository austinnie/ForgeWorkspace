# 🎎 ArtForge Ultimate (ForgeWorkspace)

> **🚀 工业级 AI 创作与自动化编排引擎**  
> **✨ 双引擎驱动 (Local/API) · 海量结构化预设 (7层架构) · 微内核技能调度 · 极致容错降级**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Dual Engine](https://img.shields.io/badge/Engine-Local%20SD%20%26%2010%2B%20APIs-green)]()
[![Presets](https://img.shields.io/badge/Presets-500%2B%20Structured%20Layers-purple)]()
[![Architecture](https://img.shields.io/badge/Architecture-Microkernel%20Skill%20System-orange)]()

---

## 🏛️ 架构全景图 (Architecture Overview)

ArtForge 并非简单的脚本集合，而是一个采用**微内核架构 (Microkernel Architecture)** 的全栈 AI 工作流引擎。其核心设计实现了业务逻辑与底层算力的完全解耦：

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         🖥️ 表现层 (Presentation Layer)                      │
│   Gradio Web UI  /  Tkinter 桌面客户端  /  CLI 命令行自动化流水线 (Pipelines)  │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │ (统一参数注入 & 动态表单渲染)
┌──────────────────────────────▼──────────────────────────────────────────────┐
│                      🧠 核心基盘：ForgeCore (微内核)                        │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌───────────────────┐  │
│  │ 🧩 Skill Manager     │  │ ⚙️ Engine Abstraction│  │ 🎨 Preset Engine  │  │
│  │ - meta.json 动态扫描 │  │ - 统一 create_engine │  │ - 7层提示词组合   │  │
│  │ - 依赖注入与校验     │  │ - API / Local 无缝切 │  │ - 智能回退与缓存  │  │
│  └──────────┬───────────┘  └──────────┬───────────┘  └─────────┬─────────┘  │
└─────────────┼──────────────────────────┼────────────────────────┼────────────┘
              │                          │                        │
┌─────────────▼──────────┐  ┌────────────▼──────────────────────┐ │
│ 📦 90+ 原子技能库      │  │ 🔌 双引擎驱动矩阵 (Dual Engines)  │ │
│ - controlnet_img2img   │  │ ☁️ API: Agnes, Pollinations,      │ │
│ - wechat_formatter     │  │      SiliconFlow, OpenRouter...   │◄┘
│ - code_gen_from_md     │  │ 💻 Local: Diffusers (SD1.5/SDXL), │
│ - stock_analyzer       │  │         ControlNet (10+ 类型)     │
└────────────────────────┘  └───────────────────────────────────┘
```

---

## 🌟 核心架构与工程亮点 (Core Highlights)

### 1. 🔌 真正的双引擎抽象层 (Engine Abstraction Layer)
彻底解决“本地部署太重，API 调用太散”的痛点。通过 `create_engine` 工厂方法，业务代码**无需关心底层实现**，即可在云端与本地间无缝切换：
*   **☁️ 云端 API 矩阵 (10+ 支持)**：深度适配 `Agnes AI` (内置多路由故障转移机制), `Pollinations` (免费), `SiliconFlow`, `OpenRouter`, `Replicate`, `Stability AI`，`SiCore TokenWorks` 等。
*   **💻 本地离线引擎**：基于 `Diffusers`，完美支持 `.safetensors` / `.ckpt` 单文件加载 (`from_single_file`)。内置 **10+ 种 ControlNet** (`canny`, `openpose`, `depth`, `hed`, `lineart`, `mlsd`, `seg`, `scribble` 等)，支持 Pipeline 缓存，重复调用无需重复加载模型。

### 2. 🎨 海量结构化预设库 (Massive Structured Presets)
这不是简单的 Prompt 列表，而是一个**三层目录结构、支持 7 层提示词架构**的庞大资产库 (`shared_assets/presets_by_app/`)，包含 **500+** 精心调优的预设：
*   **7 层提示词架构**：`subject` (主体) → `scene` (场景) → `style` (画风) → `lighting` (光影) → `composition` (构图) → `inscription` (题词印章) → `quality` (画质)。
*   **丰富的主题生态**：
    *   `oriental_forge` (东方艺术): 飞天、唐仕女、伯牙、竹林七贤、梅兰竹菊。
    *   `anime_forge` / `sculpture_forge` (二次元/雕刻): 九尾狐、天狗、雪女、玉藻前、浮世绘。
    *   `photography_forge` (国风摄影): 端午、中秋、仕女、文人、青铜、瓷器、甲胄。
    *   `mecha_forge` / `sketch_forge` (机甲/线稿): 赛博朋克、动态原型、机甲蓝图。
*   **智能组合与回退**：`PresetEngine` 自动扫描加载，当某一层缺失时，智能回退到 `default_layers`，并自带内存缓存加速读取。

### 3. 🧩 微内核技能调度系统 (Microkernel Skill System)
所有功能被封装为独立的“原子技能 (Atomic Skills)”，遵循严格的契约：
*   **零代码注册**：只需在技能目录下放置 `meta.json`，`SkillManager` 启动时自动扫描、解析参数类型并注册。
*   **统一调用入口**：`skill_manager.run("skill_name", **kwargs)`，自动处理依赖检查、参数校验、日志追踪与结果格式化。
*   **动态 GUI 渲染**：前端 UI 可直接读取 `meta.json`，动态生成对应的输入组件（文本框、下拉菜单、滑块、图片上传），实现“新增技能，UI 自动适配”。

### 4. 🛡️ 工业级容错与优雅降级 (Enterprise-grade Fallback)
代码中充满了在真实生产环境中“踩过坑”后留下的防御性设计：
*   **API 路由自动故障转移**：`AgnesEngine` 内置多个路由，当主节点超时或失败时，自动标记并切换至备用节点重试。
*   **PDF 生成三级降级**：`WeasyPrint` (完美排版) ➡️ 降级 ➡️ `xhtml2pdf` (纯 Python 兼容) ➡️ 终极降级 ➡️ `ReportLab` (保底)。配合 Base64 图片内嵌技术，彻底解决本地 PDF 库中文路径乱码的世纪难题。
*   **LLM 思维链防截断**：针对本地推理模型 (如 DeepSeek-R1 / QwQ)，当检测到 `reasoning_content` 挤占 `max_tokens` 导致正文截断时，自动扩容 4 倍预算并静默重试。
*   **对抗微信编辑器**：`wechat_formatter` 深入对抗微信后台机制，通过正则动态注入 `&nbsp;` 与 `<br>` 完美保留代码块缩进，并在无 CSS/JS 环境下硬编码实现纯内联语法高亮。

### 5. 🤖 AI 代码生成的“微型 CI/CD 闭环”
`code_gen_from_md` 超越了简单的 Prompt-to-Code，实现了一套**带验收标准的 Agent 交付流**：
*   **需求覆盖率追踪**：量化解析 MD 中的需求点，追踪 AI 实际实现的比例 (`trace.coverage`)。
*   **自动化质量门禁**：生成后自动触发 `black` 格式化、`pylint` 扫描，输出 `quality.score`。

---

## 🚀 快速开始 (Quick Start)

### 1. 环境准备
```bash
git clone <your-repo-url>
cd ForgeWorkspace
pip install -r requirements.txt
# (可选) 本地生图依赖: pip install diffusers transformers accelerate controlnet-aux safetensors
# (可选) 本地大模型: ollama pull qwen2.5:7b
```

### 2. 配置环境变量
在项目根目录创建 `.env` 文件：
```env
# ============================================================
# ArtForge 环境变量模板
# ============================================================
# 复制为 .env 并填入真实值：
#   cp .env.sample .env
# ============================================================


# ================= 路径配置 =================
# 核心模型基目录 (绝对路径)
BASE_MODELS_DIR=E:\SD_OpenVINO\models

# ================= 引擎配置 =================
# 是否使用本地模型 (true: 使用本地 OpenVINO/Diffusers, false: 使用云端 API)
USE_LOCAL_MODEL=false

# 本地推理设备 (CPU, GPU, AUTO)
LOCAL_DEVICE=CPU

   
# ---------- 生成模式 ----------
# api   = 调用云端 API（推荐）
# local = 本地 Stable Diffusion（需另装）
GENERATION_MODE=api

# 默认 API 引擎
# agnes / pollinations / siliconflow / huggingface / replicate / stability
DEFAULT_ENGINE=agnes


# ---------- 默认生成参数 ----------
DEFAULT_WIDTH=1024
DEFAULT_HEIGHT=1024
DEFAULT_STEPS=25
DEFAULT_CFG=7.5

# 默认画幅：立轴 / 横卷 / 屏风 / 团扇 / 册页
DEFAULT_SCROLL=立轴

# 默认题词格式：hanshi / waka / haiku / tiba / kuanshi
DEFAULT_INSCRIPTION=waka

# 默认印章位置：右下 / 左下 / 右上 / 左上
DEFAULT_SEAL_POSITION=左下

# 默认纸张纹理：xuan_paper / silk / aged_paper / brown_paper
DEFAULT_TEXTURE=xuan_paper


# ---------- 安全 ----------
SAFE_MODE=true
ENABLE_SAFETY_CHECK=true

# 艺术裸体主题（默认关闭，仅传统东方美学范畴）
ALLOW_ART_NUDE=false


# ---------- LLM（题词生成） ----------
LLM_ENABLED=true
LLM_BACKENDS=agnes,ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
LLM_TIMEOUT=120
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048


# ---------- Agnes AI（推荐，免费） ----------
# 注册：https://platform.agnes-ai.com/
AGNES_API_KEY=
AGNES_BASE_URL=https://apihub.agnes-ai.com/v1
AGNES_IMAGE_MODEL=agnes-image-2.1-flash
AGNES_TEXT_MODEL=agnes-2.5-flash
AGNES_VISION_MODEL=agnes-2.5-flash

# deepseek API keys
# https://platform.deepseek.com/api_keys
DEEPSEEK_API_KEY=


# google maps platform， 后期地图应用扩展
GOOGLE_API_KEY=




# ---------- Pollinations（免费，无需 Key） ----------
POLLINATIONS_MODEL=
POLLINATIONS_API_KEY=


# ---------- 硅基流动（免费额度） ----------
# 注册：https://siliconflow.cn
SILICONFLOW_API_KEY=
SILICONFLOW_MODEL=sd-turbo


# ---------- HuggingFace（免费限速） ----------
# 获取 Token：https://huggingface.co/settings/tokens
HF_API_TOKEN=
HF_MODEL=sdxl


# ---------- Replicate（付费） ----------
REPLICATE_API_TOKEN=


# ---------- Stability AI（付费） ----------
STABILITY_API_KEY=

# ----------  SiCore TokenWorks（付费） ----------
TOKENWORKS_KEY=

# ---------- 后处理 ----------
# 题词字体（放在 assets/fonts/ 下），当前用的是小篆，可以支持更多字体库
DEFAULT_FONT=kaiti.ttf

# 印章相对画面短边的比例
SEAL_SIZE_RATIO=0.06

# 题词文字相对画面短边的比例
INSCRIPTION_SIZE_RATIO=0.025


# ---------- 微信推送（可选） ----------
WECHAT_APP_ID=
WECHAT_APP_SECRET=


# ---------- 调试 ----------
DEBUG=false
LOG_LEVEL=INFO


# PWA 访问密码， 后期部署webserver后远程web访问使用
PWA_USERNAME=
PWA_PASSWORD=
```

### 3. 体验双引擎与预设 (CLI 示例)
```bash
# 🎨 场景 A：使用海量预设 + 免费 API 引擎 (无需配置 Key)
python apps/sd_generator/cli.py --app oriental_forge --theme region --preset dragon --api --api-provider freeapi

# 💻 场景 B：使用本地 SD1.5 模型 + ControlNet 姿态控制
python apps/sd_generator/cli.py --model aiiiiii01_v10 --prompt "a warrior in armor" --steps 25 --cfg 7.5 --controlnet openpose

# 🤖 场景 C：一键运行每日自动化流水线 (生图 -> AI鉴赏写文 -> 微信排版 -> 推送草稿箱)
python scripts/daily_task.py --topic "月下松林" --count 6 --theme newspaper
```

### 4. 启动 GUI 工作台（当前Artforge这个app调用），实际底层是通用底座，可以自己设计不同的app
```bash
# 启动包含技能中心与自动化 Tab 的超级工作台
python apps/artforge/gui/app.py
```
*启动后，浏览器将自动打开 `http://127.0.0.1:7860`，界面将自动加载所有预设库与本地模型。*

---

## 💻 开发者指南 (For Developers)

### 🔌 引擎抽象层调用示例
无需修改业务逻辑，即可切换算力来源：
```python
from forgecore.engines import create_engine

# 1. 使用云端 API (Agnes)
api_engine = create_engine("agnes", {"AGNES_API_KEY": "..."})
image = api_engine.text_to_image(prompt="cyberpunk city", width=1024, height=1024)

# 2. 无缝切换至本地 Diffusers (SD1.5)
local_engine = create_engine("local_sd15", {"model_path": "path/to/model.safetensors"})
image = local_engine.generate(prompt="cyberpunk city", width=512, height=768, controlnet_type="canny")
```

### 🧩 3 步添加一个新技能 (Skill)，目前已有近100个skills
1. 在 `forgecore/skills/` 下新建目录 `my_awesome_skill/`。
2. 创建 `meta.json` 定义契约：
   ```json
   {
     "name": "my_awesome_skill",
     "description": "我的第一个 AI 技能",
     "inputs": [{"name": "prompt", "type": "string", "required": true}],
     "outputs": [{"name": "result", "description": "生成结果"}],
     "dependencies": ["requests"]
   }
   ```
3. 创建 `skill.py` 实现逻辑：
   ```python
   from forgecore.skills.base import BaseSkill
   
   class MyAwesomeSkill(BaseSkill):
       def execute(self, **kwargs):
           return {"status": "success", "result": f"Processed: {kwargs.get('prompt')}"}
   ```
*重启应用，`SkillManager` 会自动扫描、校验并将其暴露在 CLI 和 GUI 中。*

---

## 📂 核心目录结构

```text
ForgeWorkspace/
├── apps/                     # 🖥️ 表现层应用
│   └── artforge/             # GUI 界面 (核心生图 / 超级工作台 unified_app.py)
├── forgecore/                # 🧠 微内核基盘 (MarkFlow Engine)
│   ├── engines/              # 🔌 引擎抽象层 (agnes, pollinations, local_diffusers 等)
│   ├── skills/               # 🧩 90+ 原子技能库 (完全解耦，基于 meta.json)
│   │   ├── controlnet_img2img/ # ControlNet 底层通用引擎
│   │   ├── wechat_formatter/   # 微信排版技能 (含极致对抗逻辑)
│   │   └── code_gen_from_md/   # 代码生成技能 (含微型 CI/CD)
│   ├── prompt/               # 🎨 PresetEngine (7层预设组合与缓存引擎)
│   └── post_process/         # 🖌️ 后期处理 (古画做旧 / 题词 / 印章生成 / 水印)
├── scripts/                  # 🤖 自动化流水线 (ai_mv.py, daily_task.py)
├── shared_assets/            # 📦 共享资产中心
│   └── presets_by_app/       # 🌟 海量预设库 (oriental_forge, anime_forge 等 500+ 预设)
├── models/                   # 💾 本地模型目录 (SD1.5 / SDXL / ControlNet)
└── output/                   # 📤 产物输出目录
```

---

## 🤝 贡献与许可证 (License)

> *"AI 的价值不在于能调用多少个 API，而在于当网络波动、依赖缺失、模型截断、平台限制时，你的代码是否依然能优雅地降级并交付结果。"*

本项目采用 **MIT License** 开源协议。仅供学习与研究使用，使用本项目生成的内容请遵守相关法律法规及 AI 模型的使用协议。

欢迎提交 Issue 和 Pull Request！如果你想分享你编写的原子技能或预设，请确保包含完整的 `meta.json` 或符合 7 层架构的 `.py` 文件。

**Copyright © 2026 ArtForge Team. All rights reserved.**
