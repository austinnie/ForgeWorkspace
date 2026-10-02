# gui/app.py
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageTk

# 确保路径正确
APP_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_ROOT.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 导入 ForgeCore 基座
try:
    from forgecore.config.paths import Paths
    from forgecore.config.registry import ModelRegistry
    from forgecore.config.settings import settings
    from forgecore.engines import create_engine
    from forgecore.engines.local_engine import DiffusersEngine
except ImportError as e:
    print(f"❌ 无法导入 ForgeCore: {e}")
    sys.exit(1)

class SDGuiApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SD GUI (ForgeCore Thin Shell)")
        self.root.geometry("1100x750")
        
        self.presets = self._scan_presets()
        self.local_models = self._scan_models()
        self.api_providers = ["freeapi", "pollinations", "agnes", "siliconflow", "tongyi", "hunyuan"]
        
        self._build_ui()
        self._update_engine_visibility()
        
    def _scan_presets(self):
        presets = []
        presets_base = PROJECT_ROOT / "shared_assets" / "presets_by_app"
        if not presets_base.exists():
            return presets
        for app_dir in sorted(presets_base.iterdir()):
            if not app_dir.is_dir() or app_dir.name.startswith('_'): continue
            for theme_dir in sorted(app_dir.iterdir()):
                if not theme_dir.is_dir() or theme_dir.name.startswith('_'): continue
                for py_file in sorted(theme_dir.glob("*.py")):
                    if py_file.name.startswith('_') or py_file.name == '__init__.py': continue
                    rel_id = f"{app_dir.name}/{theme_dir.name}/{py_file.stem}"
                    presets.append(rel_id)
        return presets

    def _scan_models(self):
        models = []
        try:
            sd15 = ModelRegistry.scan_checkpoints("sd15")
            sdxl = ModelRegistry.scan_checkpoints("sdxl")
            for m in sd15:
                models.append({"name": m["name"], "path": m["absolute_path"], "type": "sd15"})
            for m in sdxl:
                models.append({"name": m["name"], "path": m["absolute_path"], "type": "sdxl"})
        except Exception as e:
            print(f"⚠️ 扫描模型失败: {e}")
        return models

    def _build_ui(self):
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_paned, width=400)
        main_paned.add(left_frame, weight=1)

        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)

        eng_frame = ttk.LabelFrame(left_frame, text="🔌 引擎配置 (Local / API)")
        eng_frame.pack(fill=tk.X, pady=5)
        
        self.engine_mode = tk.StringVar(value="api")
        ttk.Radiobutton(eng_frame, text="☁️ API 引擎 (免配置/快速)", variable=self.engine_mode, value="api", command=self._update_engine_visibility).pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(eng_frame, text="💻 本地模型 (SD1.5/SDXL)", variable=self.engine_mode, value="local", command=self._update_engine_visibility).pack(anchor=tk.W, padx=5)

        self.api_frame = ttk.Frame(eng_frame)
        self.api_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(self.api_frame, text="Provider:").pack(side=tk.LEFT)
        self.api_provider_cb = ttk.Combobox(self.api_frame, values=self.api_providers, state="readonly", width=20)
        self.api_provider_cb.pack(side=tk.LEFT, padx=5)
        self.api_provider_cb.set("freeapi") # 默认选免费引擎

        self.local_frame = ttk.Frame(eng_frame)
        self.local_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(self.local_frame, text="Model:").pack(side=tk.LEFT)
        self.local_model_cb = ttk.Combobox(self.local_frame, values=[m["name"] for m in self.local_models], state="readonly", width=30)
        self.local_model_cb.pack(side=tk.LEFT, padx=5)
        if self.local_models:
            self.local_model_cb.set(self.local_models[0]["name"])

        preset_frame = ttk.LabelFrame(left_frame, text="🎨 预设 (来自 shared_assets)")
        preset_frame.pack(fill=tk.X, pady=5)
        self.preset_cb = ttk.Combobox(preset_frame, values=self.presets, state="readonly")
        self.preset_cb.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(preset_frame, text="⬇️ 加载预设到提示词", command=self._load_preset_to_prompt).pack(fill=tk.X, padx=5, pady=(0,5))

        prompt_frame = ttk.LabelFrame(left_frame, text="📝 提示词")
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(prompt_frame, text="Positive:").pack(anchor=tk.W, padx=5)
        self.prompt_text = tk.Text(prompt_frame, height=5, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        ttk.Label(prompt_frame, text="Negative:").pack(anchor=tk.W, padx=5)
        self.neg_text = tk.Text(prompt_frame, height=2, wrap=tk.WORD)
        self.neg_text.pack(fill=tk.X, padx=5, pady=2)
        self.neg_text.insert("1.0", "worst quality, low quality, ugly, deformed, blurry, bad anatomy, watermark, text")

        param_frame = ttk.LabelFrame(left_frame, text="⚙️ 生成参数")
        param_frame.pack(fill=tk.X, pady=5)
        grid = ttk.Frame(param_frame)
        grid.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(grid, text="Steps:").grid(row=0, column=0, sticky=tk.W)
        self.steps_var = tk.IntVar(value=20)
        ttk.Spinbox(grid, from_=1, to=100, textvariable=self.steps_var, width=5).grid(row=0, column=1, padx=5)
        
        ttk.Label(grid, text="CFG:").grid(row=0, column=2, sticky=tk.W)
        self.cfg_var = tk.DoubleVar(value=7.5)
        ttk.Spinbox(grid, from_=1.0, to=20.0, increment=0.5, textvariable=self.cfg_var, width=5).grid(row=0, column=3, padx=5)

        ttk.Label(grid, text="Width:").grid(row=1, column=0, sticky=tk.W)
        self.width_var = tk.IntVar(value=512)
        ttk.Spinbox(grid, from_=256, to=1024, increment=64, textvariable=self.width_var, width=5).grid(row=1, column=1, padx=5)

        ttk.Label(grid, text="Height:").grid(row=1, column=2, sticky=tk.W)
        self.height_var = tk.IntVar(value=768)
        ttk.Spinbox(grid, from_=256, to=1024, increment=64, textvariable=self.height_var, width=5).grid(row=1, column=3, padx=5)

        ttk.Label(grid, text="Seed:").grid(row=2, column=0, sticky=tk.W)
        self.seed_var = tk.StringVar(value="-1")
        ttk.Entry(grid, textvariable=self.seed_var, width=15).grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5)

        self.gen_btn = ttk.Button(left_frame, text="🚀 生成图片", command=self._start_generate)
        self.gen_btn.pack(fill=tk.X, pady=10)

        # --- 右侧 UI ---
        self.img_label = ttk.Label(right_frame, text="预览区", relief=tk.SUNKEN, anchor=tk.CENTER)
        self.img_label.pack(fill=tk.BOTH, expand=True, pady=5)

        log_frame = ttk.LabelFrame(right_frame, text="📜 运行日志")
        log_frame.pack(fill=tk.X, pady=5)
        self.log_text = tk.Text(log_frame, height=10, state=tk.DISABLED, wrap=tk.WORD, bg="#f4f4f4")
        self.log_text.pack(fill=tk.X, padx=5, pady=5)

    def _update_engine_visibility(self):
        if self.engine_mode.get() == "api":
            self.api_frame.pack(fill=tk.X, padx=5, pady=2)
            self.local_frame.pack_forget()
        else:
            self.local_frame.pack(fill=tk.X, padx=5, pady=2)
            self.api_frame.pack_forget()

    def _load_preset_to_prompt(self):
        import importlib.util
        preset_id = self.preset_cb.get()
        if not preset_id: return
        parts = preset_id.split('/')
        if len(parts) != 3: return
            
        app_dir, theme_dir, name = parts
        py_file = PROJECT_ROOT / "shared_assets" / "presets_by_app" / app_dir / theme_dir / f"{name}.py"
        
        try:
            spec = importlib.util.spec_from_file_location(name, py_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            preset_data = getattr(mod, "PRESET", {})
            layers = preset_data.get("layers", {})
            prompt_parts = []
            for key in ["subject", "scene", "style", "lighting", "view", "quality"]:
                if key in layers and isinstance(layers[key], list):
                    prompt_parts.extend(layers[key])
            prompt = ", ".join(prompt_parts)
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", prompt)
            self._log(f"✅ 已加载预设: {preset_id}")
        except Exception as e:
            self._log(f"❌ 加载预设失败: {e}")

    def _log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _start_generate(self):
        self.gen_btn.config(state=tk.DISABLED)
        self._log("🚀 任务已提交，正在后台生成...")
        threading.Thread(target=self._run_generate, daemon=True).start()

    def _run_generate(self):
        try:
            mode = self.engine_mode.get()
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            negative = self.neg_text.get("1.0", tk.END).strip()
            steps = self.steps_var.get()
            cfg = self.cfg_var.get()
            w = self.width_var.get()
            h = self.height_var.get()
            seed_str = self.seed_var.get()
            seed = int(seed_str) if seed_str.isdigit() else -1

            if not prompt:
                raise ValueError("提示词不能为空")

            img = None
            
            if mode == "local":
                model_name = self.local_model_cb.get()
                model_info = next((m for m in self.local_models if m["name"] == model_name), None)
                if not model_info:
                    raise ValueError("未选择本地模型")
                
                self.root.after(0, self._log, f"💻 加载本地模型: {model_name} (首次可能需要30秒)...")
                engine = DiffusersEngine(model_type=model_info["type"], device="CPU")
                engine.load_model(model_info["path"])
                
                self.root.after(0, self._log, f"🎨 本地推理中 (steps={steps}, cfg={cfg})...")
                img = engine.generate(
                    prompt=prompt, negative_prompt=negative,
                    width=w, height=h, steps=steps, cfg=cfg, seed=seed
                )
            else:
                provider = self.api_provider_cb.get()
                
                # ⚠️ 前置校验：如果是 Agnes 且没 Key，直接报错
                if provider == "agnes" and not os.getenv("AGNES_API_KEY"):
                    raise ValueError("❌ 检测到使用 Agnes 但未配置 AGNES_API_KEY。请在 .env 文件中配置，或切换到 freeapi/pollinations。")

                self.root.after(0, self._log, f"☁️ 调用 API: {provider}...")
                
                config = {
                    "AGNES_API_KEY": os.getenv("AGNES_API_KEY", ""),
                    "AGNES_BASE_URL": os.getenv("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1"),
                    "AGNES_IMAGE_MODEL": os.getenv("AGNES_IMAGE_MODEL", "agnes-image-2.1-flash"),
                    "FREEAPI_MODEL": os.getenv("FREEAPI_MODEL", "grok-imagine-image-lite"),
                    "POLLINATIONS_MODEL": os.getenv("POLLINATIONS_MODEL", "flux"),
                    "SILICONFLOW_API_KEY": os.getenv("SILICONFLOW_API_KEY", ""),
                    "SILICONFLOW_MODEL": os.getenv("SILICONFLOW_MODEL", "FLUX.1-dev"),
                }
                engine = create_engine(provider, config=config)
                
                # API 引擎统一使用 generate_single
                img = engine.generate_single(
                    prompt=prompt, negative=negative,
                    width=w, height=h, steps=steps, cfg=cfg, seed=seed
                )

            if img:
                Paths.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = Paths.OUTPUT_DIR / f"sdgui_{timestamp}.png"
                img.save(save_path)
                
                self.root.after(0, self._show_image, img)
                self.root.after(0, self._log, f"✅ 生成成功！保存至: {save_path}")
            else:
                self.root.after(0, self._log, "❌ 引擎未返回图片")

        except Exception as e:
            import traceback
            self.root.after(0, self._log, f"❌ 生成失败: {e}\n{traceback.format_exc()}")
        finally:
            self.root.after(0, lambda: self.gen_btn.config(state=tk.NORMAL))

    def _show_image(self, pil_img):
        max_w, max_h = 600, 600
        ratio = min(max_w / pil_img.width, max_h / pil_img.height)
        new_size = (int(pil_img.width * ratio), int(pil_img.height * ratio))
        resized = pil_img.resize(new_size, Image.Resampling.LANCZOS)
        self._tk_img = ImageTk.PhotoImage(resized)
        self.img_label.config(image=self._tk_img, text="")

    def run(self):
        self.root.mainloop()