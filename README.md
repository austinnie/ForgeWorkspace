# 🎎 ArtForge Ultimate (ForgeWorkspace)

**ArtForge Ultimate** 是一个基于 `ForgeCore` 基盘构建的全能 AI 创作工作台。它集成了东方美学生成、图生图/ControlNet、像素级魔法编辑、自动化视频/漫画流水线以及 90+ 原子技能调度系统。

本项目旨在将零散的 AI 能力（生图、视频、音乐、排版、发布）串联成**一键式的自动化生产线**，同时提供高度可定制的 GUI 界面。

---

## 🌟 核心特性 (Features)

### 🎨 1. 东方艺术生成工坊
- **6层提示词架构**：主体、场景、风格、光影、构图、质量精准控制。
- **动态预设库**：支持多主题库（如 `oriental_forge`, `anime_forge`）动态扫描与加载。
- **专业后期流水线**：自动装裱（立轴/横卷/屏风）、古画做旧（宣纸纹理）、竖排题词、印章生成、隐形水印。

### 🖼️ 2. 图生图 & ControlNet 工作台
- **双引擎支持**：默认接入 Agnes API 图生图，无缝切换本地 SD1.5/SDXL 模型。
- **ControlNet 集成**：支持 OpenPose、Canny、Depth、Lineart 等多种控制类型，精准锁定参考图特征。

###  3. 像素魔法 (Pixel Magic)
- **一键局部编辑**：无需编写提示词，上传参考图即可实现加眼镜、换发型、换背景、去马赛克等 50+ 种像素级操作。
- **智能降级路由**：API 模式下自动模拟 Prompt 图生图，本地模式下调用专属 ControlNet/Inpainting Skill。

### 🚀 4. 自动化工作流 (Pipelines)
- **AI 视频/MV 创作**：批量出图 → 图片合成视频 → AI 生成配乐 → 音视频合并 → 自动发布视频号/B站。
- **每日研报/推文自动生成**：资讯抓取 → AI 撰写 → 封面生成 → 微信排版 → 多平台分发。
- **无人值守模式**：支持从主题池自动轮询主题，配合 Windows 任务计划程序实现全自动日更。

### 🛠️ 5. 全局技能中心 (Skill Hub)
- **90+ 原子技能**：涵盖图像编辑、文档处理、多媒体播放、搜索聚合等。
- **SkillManager 统一调度**：通过 `skill_manager.run("skill_name", **kwargs)` 一行代码调用任意技能。
- **动态表单 UI**：GUI 自动识别技能类型（图生图/文生图/文本处理），动态渲染输入组件。

---

## 📂 目录结构 (Project Structure)

```text
ForgeWorkspace/
├── apps/
│   └── artforge/
│       ├── gui/
│       │   ├── app.py              # 核心 GUI (东方艺术/图生图/像素魔法)
│       │   ── unified_app.py      # 超级工作台 (含技能中心与自动化 Tab)
│       └── main.py                 # 启动入口
├── forgecore/                      # 核心基盘
│   ├── config/                     # 路径、注册表、环境变量配置
│   ├── engines/                    # 引擎抽象层 (API/Local Diffusers)
│   ├── post_process/               # 后期处理 (做旧/题词/印章/水印)
│   └── skills/                     # 90+ 原子技能库
│       ├── base.py                 # Skill 基类
│       ├── manager.py              # 全局技能调度器
│       ├── controlnet/             # ControlNet 技能
│       ├── add_glasses/            # 像素魔法技能示例
│       └── ...                     # 其他 80+ 技能
├── scripts/                        # 自动化流水线脚本
│   ├── ai_mv.py                    # AI 音乐 MV 生成流水线
│   ├── amway_daily.py              # 每日产品推送流水线
│   ├── add_music_to_video.py       # 视频自动配乐工具
│   └── html_to_pdf.py              # HTML 转 PDF 工具
├── shared_assets/                  # 共享资源
│   └── presets_by_app/             # 预设库 (按应用分类)
├── models/                         # 模型目录 (SD1.5/SDXL/ControlNet/LoRA)
├── output/                         # 产物输出目录
└── .env                            # 环境变量 (API Keys 等)
```
## 🚀 快速开始 (Quick Start)

### 1. 环境准备
确保已安装 Python 3.10+ 及必要的依赖（如 `gradio`, `diffusers`, `torch`, `pillow` 等）。

### 2. 配置环境变量
在项目根目录创建 `.env` 文件，配置必要的 API Keys：

```env
AGNES_API_KEY=your_agnes_api_key
AGNES_BASE_URL=https://apihub.agnes-ai.com/v1
# 其他 API Keys...
```
### 3. 启动 GUI 工作台
```bash
# 启动核心 ArtForge 界面
python apps/artforge/main.py

# 或启动包含技能中心的超级工作台
python apps/artforge/gui/unified_app.py
```

启动后，浏览器将自动打开 http://127.0.0.1:7860。

### 4. 运行自动化流水线
```bash
# 运行 AI MV 生成流水线
python scripts/ai_mv.py --category tang --presets dunhuang feitian --title "敦煌飞天" --duration 40

# 运行每日研报自动生成 (自动选择主题)
python scripts/daily_insight_pipeline.py --mode queue
```

### ⚙️ 核心模块说明
SkillManager (技能调度器)
所有技能均继承自 BaseSkill，并通过 SkillManager 进行统一注册和调用。
```python
from forgecore.skills import skill_manager

# 扫描所有技能
skill_manager.scan()

# 调用任意技能
result = skill_manager.run(
    "add_glasses", 
    image_path="input.jpg", 
    output_path="output.jpg",
    model_path="path/to/model"
)

if result["status"] == "success":
    print("生成成功:", result["result"]["output_path"])
```

### 引擎抽象层 (Engines)
支持 API 引擎（Agnes, Pollinations）和本地 Diffusers 引擎的统一调用接口。
```python
from forgecore.engines import create_engine

# 创建 API 引擎
engine = create_engine("agnes", {"AGNES_API_KEY": "..."})
image = engine.image_to_image(prompt="...", image=ref_img, strength=0.6)

# 创建本地引擎
engine = create_engine("local_sd15", {"model_path": "..."})
image = engine.generate(prompt="...", width=512, height=768)
```


### 🛠️ 配置与扩展
添加新技能
在 forgecore/skills/ 下新建目录（如 my_new_skill）。
创建 skill.py 并继承 BaseSkill，实现 execute 方法。
创建 meta.json 描述技能元信息。
重启应用，SkillManager 会自动扫描并加载新技能。
添加新预设
在 shared_assets/presets_by_app/ 下新建主题目录。
创建 Python 文件定义 PRESET 字典（包含 subject, scene, style 等 layers）。
在 GUI 的“预设库”下拉框中即可选择新预设。

### 许可证 (License)
本项目仅供学习与研究使用。使用本项目生成的内容请遵守相关法律法规及 AI 模型的使用协议。
Copyright © 2026 ArtForge Team. All rights reserved.