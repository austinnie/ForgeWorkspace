"""
ControlNet - 提供姿态检测和 ControlNet 控制能力
支持 10 种 ControlNet 类型，Pipeline 生图，批量处理
"""

import os

# [ForgeCore 兼容] 全局默认模型路径，可通过环境变量覆盖
SD_MODEL_PATH = os.environ.get('SD_MODEL_PATH', None)

import os
import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
import logging

logger = logging.getLogger(__name__)

# ==================== 🔥 修复 mediapipe API 不兼容 ====================
try:
    import mediapipe as mp
    if not hasattr(mp, 'solutions'):
        from types import SimpleNamespace
        
        # 创建所有需要的 mock 对象
        mp.solutions = SimpleNamespace(
            # 基础 drawing
            drawing_utils=SimpleNamespace(
                _normalized_to_pixel_coordinates=lambda *args, **kwargs: None,
                draw_landmarks=lambda *args, **kwargs: None,
                draw_axis=lambda *args, **kwargs: None,
            ),
            drawing_styles=SimpleNamespace(
                get_default_face_mesh_tesselation_style=lambda: None,
                get_default_face_mesh_contours_style=lambda: None,
                get_default_face_mesh_iris_connections_style=lambda: None,
            ),
            # face_detection
            face_detection=SimpleNamespace(
                FaceDetection=lambda *args, **kwargs: SimpleNamespace(
                    process=lambda *args, **kwargs: SimpleNamespace(
                        detections=[]
                    )
                )
            ),
            # face_mesh
            face_mesh=SimpleNamespace(
                FaceMesh=lambda *args, **kwargs: SimpleNamespace(
                    process=lambda *args, **kwargs: SimpleNamespace(
                        multi_face_landmarks=[]
                    )
                ),
                FACEMESH_TESSELATION=[],
                FACEMESH_CONTOURS=[],
                FACEMESH_IRIS=[],
            ),
            face_mesh_connections=SimpleNamespace(
                FACEMESH_TESSELATION=[],
                FACEMESH_CONTOURS=[],
                FACEMESH_IRIS=[],
            ),
            # pose
            pose=SimpleNamespace(
                Pose=lambda *args, **kwargs: SimpleNamespace(
                    process=lambda *args, **kwargs: SimpleNamespace(
                        pose_landmarks=None
                    )
                ),
                POSE_CONNECTIONS=[],
            ),
            # hands
            hands=SimpleNamespace(
                Hands=lambda *args, **kwargs: SimpleNamespace(
                    process=lambda *args, **kwargs: SimpleNamespace(
                        multi_hand_landmarks=[]
                    )
                ),
                HAND_CONNECTIONS=[],
            ),
            # holistic
            holistic=SimpleNamespace(
                Holistic=lambda *args, **kwargs: SimpleNamespace(
                    process=lambda *args, **kwargs: SimpleNamespace(
                        pose_landmarks=None,
                        face_landmarks=None,
                        left_hand_landmarks=None,
                        right_hand_landmarks=None,
                    )
                ),
                POSE_CONNECTIONS=[],
                FACE_CONNECTIONS=[],
            ),
        )
        print("⚠️ mediapipe.solutions 已 mock (新版 API 兼容)")
except ImportError:
    pass
    
# ==================== 依赖检查 ====================
try:
    import torch
    import numpy as np
    from PIL import Image
    import cv2
    TORCH_AVAILABLE = True
except ImportError as e:
    TORCH_AVAILABLE = False
    logger.warning(f"基础依赖未安装: {e}")

import os
os.environ["MEDIAPIPE_DISABLE_GPU"] = "1"  # 禁用 mediapipe GPU 加速

try:
    from diffusers import ControlNetModel, StableDiffusionControlNetPipeline
    DIFFUSERS_AVAILABLE = True
except ImportError as e:
    DIFFUSERS_AVAILABLE = False
    logger.warning(f"diffusers 未安装: {e}")

try:
    from controlnet_aux import (
        OpenposeDetector,
        CannyDetector,
        HEDdetector,
        MidasDetector,
        LineartDetector,
        NormalBaeDetector,
        MLSDdetector,
        DWposeDetector,
    )
    # 尝试导入新增的检测器
    try:
        from controlnet_aux import (SegDetector, UniformerDetector)
        SEG_AVAILABLE = True
    except ImportError:
        SEG_AVAILABLE = False
        logger.warning("SegDetector/UniformerDetector 不可用，请更新 controlnet-aux")
    
    CONTROLNET_AUX_AVAILABLE = True
except ImportError as e:
    CONTROLNET_AUX_AVAILABLE = False
    SEG_AVAILABLE = False
    logger.warning(f"controlnet_aux 未安装: {e}")


# ==================== ControlNet 类型配置 ====================
CONTROLNET_TYPES = {
    # ===== 原有类型 =====
    "canny": {
        "name": "Canny (边缘)",
        "model_id": "lllyasviel/sd-controlnet-canny",
        "preprocessor": "canny",
        "description": "边缘轮廓控制，适合保持构图"
    },
    "hed": {
        "name": "HED (软边缘)",
        "model_id": "lllyasviel/sd-controlnet-hed",
        "preprocessor": "hed",
        "description": "软边缘检测，更灵活"
    },
    "lineart": {
        "name": "Lineart (线稿)",
        "model_id": "lllyasviel/control_v11p_sd15_lineart",
        "preprocessor": "lineart",
        "description": "线稿提取，适合二次元"
    },
    "depth": {
        "name": "Depth (深度)",
        "model_id": "lllyasviel/sd-controlnet-depth",
        "preprocessor": "depth",
        "description": "深度图控制，适合保持空间结构"
    },
    "normal": {
        "name": "Normal (法线)",
        "model_id": "lllyasviel/sd-controlnet-normal",
        "preprocessor": "normal",
        "description": "法线图控制，适合保持光影"
    },
    "mlsd": {
        "name": "MLSD (直线)",
        "model_id": "lllyasviel/sd-controlnet-mlsd",
        "preprocessor": "mlsd",
        "description": "直线检测，适合建筑"
    },
    "openpose": {
        "name": "OpenPose (姿态)",
        "model_id": "lllyasviel/sd-controlnet-openpose",
        "preprocessor": "openpose",
        "description": "检测人体姿态骨架，适合换装"
    },
    "openpose_full": {
        "name": "OpenPose Full (完整姿态)",
        "model_id": "lllyasviel/control_v11p_sd15_openpose",
        "preprocessor": "openpose_full",
        "description": "全身姿态 + 手指 + 面部表情"
    },
    
    # ===== 新增类型 =====
    "seg": {
        "name": "Segmentation (语义分割)",
        "model_id": "lllyasviel/sd-controlnet-seg",
        "preprocessor": "seg",
        "description": "语义分割控制，适合换背景、场景转换"
    },
    "scribble": {
        "name": "Scribble (涂鸦)",
        "model_id": "lllyasviel/sd-controlnet-scribble",
        "preprocessor": "scribble",
        "description": "涂鸦控制，适合手绘控制"
    },
}


class Controlnet:
    """
    ControlNet 技能

    提供:
        1. 姿态检测 (detect_pose)
        2. ControlNet Pipeline 加载 (load_pipeline)
        3. 图片生成 (generate)
        4. 批量处理 (batch_process)
        5. 状态查看 (status)
        6. 类型列表 (list_types)
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化 ControlNet 技能

        Args:
            config: 配置字典
                - device: 设备 (cpu/cuda)
                - max_size: 最大尺寸
                - cache_dir: 缓存目录
                - default_model_path: 默认 SD 模型路径
        """
        self.config = config or {}
        self.name = "ControlNet"
        self.version = "2.0.0"

        # 获取技能目录
        self.skill_dir = Path(__file__).parent.parent.parent.absolute()  # 回到项目根目录
        self.output_dir = self.skill_dir / "output" / "controlnet"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 配置
        self.device = self.config.get('device', 'cpu')
        self.max_size = self.config.get('max_size', 512)


        # 🆕 缓存目录：使用 HF_HOME 环境变量
        # 使用 HF_HUB_CACHE（和 cli.py 保持一致）
        #default_cache = os.environ.get('HF_HUB_CACHE', os.environ.get('HF_HOME', str(self.skill_dir / 'cache')))
        #self.cache_dir = self.config.get('cache_dir', default_cache)
        self.cache_dir = self.config.get('cache_dir', r"E:\SD_OpenVINO\models\controlnet")
        
        # ===== 🆕 自动读取 SD_MODEL_PATH =====
        # 1. 优先使用 config 传入的
        self.default_model_path = self.config.get('default_model_path', None)
        
        # 2. 如果 config 没传，尝试从项目配置文件读取
        if self.default_model_path is None:
            self.default_model_path = None  # 安全占位符
    def list_types(self) -> Dict[str, Any]:
        """列出所有支持的 ControlNet 类型"""
        types = {}
        for key, info in CONTROLNET_TYPES.items():
            types[key] = {
                "name": info["name"],
                "description": info["description"],
                "available": CONTROLNET_AUX_AVAILABLE,
            }

        return {
            "status": "success",
            "types": types,
            "count": len(types),
            "controlnet_aux_available": CONTROLNET_AUX_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        }

    def status(self) -> Dict[str, Any]:
        """查看 ControlNet 技能状态"""
        return {
            "status": "success",
            "skill": {
                "name": self.name,
                "version": self.version,
                "device": self.device,
                "max_size": self.max_size,
                "cache_dir": self.cache_dir,
                "default_model_path": self.default_model_path,
            },
            "dependencies": {
                "diffusers": DIFFUSERS_AVAILABLE,
                "controlnet_aux": CONTROLNET_AUX_AVAILABLE,
                "seg_available": SEG_AVAILABLE,
                "torch": TORCH_AVAILABLE,
            },
            "supported_types": list(CONTROLNET_TYPES.keys()),
            "cached_pipelines": list(self._pipelines.keys()),
            "timestamp": datetime.now().isoformat()
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行 ControlNet 技能

        支持的操作:
            - status: 查看状态 (默认)
            - list_types: 列出支持的 ControlNet 类型
            - detect_pose: 检测姿态，生成控制图
            - load_pipeline: 加载 ControlNet Pipeline
            - generate: 一步生成图片（新增）
            - batch_detect: 批量检测（新增）
            - batch_generate: 批量生成（新增）
            - gui: 启动 Gradio UI（新增）
        """
        action = kwargs.get('action', 'status')
        logger.info(f"执行 ControlNet 技能: action={action}")

        if action == 'status':
            return self.status()

        elif action == 'list_types':
            return self.list_types()

        elif action == 'detect_pose':
            image = kwargs.get('image') or kwargs.get('image_path')
            if image is None:
                return {"status": "error", "error": "image 或 image_path 是必填参数"}
            controlnet_type = kwargs.get('controlnet_type', 'openpose')
            output_path = kwargs.get('output_path')
            return self.detect_pose(image, controlnet_type, output_path)

        elif action == 'load_pipeline':
            model_path = kwargs.get('model_path')
            if model_path is None:
                return {"status": "error", "error": "model_path 是必填参数"}
            controlnet_type = kwargs.get('controlnet_type', 'openpose')
            return self.get_pipeline(model_path, controlnet_type)

        elif action == 'generate':
            image = kwargs.get('image') or kwargs.get('image_path')
            if image is None:
                return {"status": "error", "error": "image 或 image_path 是必填参数"}
            prompt = kwargs.get('prompt')
            if prompt is None:
                return {"status": "error", "error": "prompt 是必填参数"}
            return self.generate(
                image=image,
                prompt=prompt,
                controlnet_type=kwargs.get('controlnet_type', 'openpose'),
                model_path=kwargs.get('model_path'),
                negative_prompt=kwargs.get('negative_prompt', ''),
                num_inference_steps=kwargs.get('steps', 20),
                guidance_scale=kwargs.get('cfg_scale', 7.5),
                seed=kwargs.get('seed', -1),
                controlnet_conditioning_scale=kwargs.get('controlnet_strength', 1.0),
                output_path=kwargs.get('output_path'),
                save_control=kwargs.get('save_control', True),
            )

        elif action == 'batch_detect':
            images = kwargs.get('images')
            if images is None:
                return {"status": "error", "error": "images 是必填参数"}
            if isinstance(images, str):
                images = [img.strip() for img in images.split(',')]
            return self.batch_detect_pose(
                images=images,
                controlnet_type=kwargs.get('controlnet_type', 'openpose'),
                output_dir=kwargs.get('output_dir'),
            )

        elif action == 'batch_generate':
            images = kwargs.get('images')
            prompts = kwargs.get('prompts')
            if images is None:
                return {"status": "error", "error": "images 是必填参数"}
            if prompts is None:
                return {"status": "error", "error": "prompts 是必填参数"}
            if isinstance(images, str):
                images = [img.strip() for img in images.split(',')]
            if isinstance(prompts, str):
                prompts = [p.strip() for p in prompts.split('||')]
            return self.batch_generate(
                images=images,
                prompts=prompts,
                controlnet_type=kwargs.get('controlnet_type', 'openpose'),
                model_path=kwargs.get('model_path'),
                negative_prompt=kwargs.get('negative_prompt', ''),
                num_inference_steps=kwargs.get('steps', 20),
                guidance_scale=kwargs.get('cfg_scale', 7.5),
                output_dir=kwargs.get('output_dir'),
            )

        elif action == 'gui':
            self.launch_gradio(
                share=kwargs.get('share', False),
                server_name=kwargs.get('server_name', '127.0.0.1'),
                server_port=kwargs.get('server_port', 7860),
            )
            return {"status": "success", "message": "Gradio UI 已启动"}

        else:
            return {
                "status": "error",
                "error": f"未知操作: {action}，支持: status, list_types, detect_pose, load_pipeline, generate, batch_detect, batch_generate, gui",
                "timestamp": datetime.now().isoformat()
            }

    def __repr__(self):
        return f"<Controlnet(name={self.name}, version={self.version})>"


# ==================== 命令行入口 ====================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ControlNet 技能 v2.0")
    parser.add_argument("--action", default="status",
                        choices=["status", "list_types", "detect_pose", "load_pipeline", 
                                "generate", "batch_detect", "batch_generate", "gui"],
                        help="操作类型")
    parser.add_argument("--image", help="图片路径 (detect_pose/generate)")
    parser.add_argument("--image-path", help="图片路径 (detect_pose/generate, 同 image)")
    parser.add_argument("--images", help="批量图片路径，用逗号分隔 (batch_detect/batch_generate)")
    parser.add_argument("--prompt", help="生成提示词 (generate/batch_generate)")
    parser.add_argument("--prompts", help="批量提示词，用 || 分隔 (batch_generate)")
    parser.add_argument("--output-path", help="输出路径 (detect_pose/generate)")
    parser.add_argument("--output-dir", help="输出目录 (batch_detect/batch_generate)")
    parser.add_argument("--model-path", help="SD 模型路径 (load_pipeline/generate)")
    parser.add_argument("--controlnet-type", default="openpose",
                        choices=list(CONTROLNET_TYPES.keys()),
                        help="ControlNet 类型")
    parser.add_argument("--negative-prompt", default="", help="负面提示词")
    parser.add_argument("--steps", type=int, default=20, help="推理步数")
    parser.add_argument("--cfg-scale", type=float, default=7.5, help="CFG 尺度")
    parser.add_argument("--seed", type=int, default=-1, help="随机种子 (-1 随机)")
    parser.add_argument("--controlnet-strength", type=float, default=1.0, help="ControlNet 控制强度 (0.0-1.0)")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu", help="设备")
    parser.add_argument("--share", action="store_true", help="Gradio 公开链接 (gui)")
    parser.add_argument("--port", type=int, default=7860, help="Gradio 端口 (gui)")

    args = parser.parse_args()

    skill = Controlnet(config={'device': args.device})

    if args.action == "gui":
        skill.launch_gradio(share=args.share, server_port=args.port)
    else:
        result = skill.execute(
            action=args.action,
            image=args.image or args.image_path,
            images=args.images,
            prompt=args.prompt,
            prompts=args.prompts,
            output_path=args.output_path,
            output_dir=args.output_dir,
            model_path=args.model_path,
            controlnet_type=args.controlnet_type,
            negative_prompt=args.negative_prompt,
            steps=args.steps,
            cfg_scale=args.cfg_scale,
            seed=args.seed,
            controlnet_strength=args.controlnet_strength,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))