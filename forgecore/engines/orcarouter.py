# api_engines/orcarouter.py
"""OrcaRouter 多模态引擎 - OpenAI 兼容的 AI 网关
支持：Chat 对话、图像生成、文本转语音、视频生成、Seedance 资产管理
文档：https://docs.orcarouter.ai/

支持的模型 (200+)：
- Chat: openai/gpt-4o-mini, anthropic/claude-opus-4.6, google/gemini-2.5-pro, deepseek/deepseek-v4-flash
- Image: openai/gpt-image-1, openai/dall-e-3, google/imagen-4.0-standard-generate-001
- Video: kling/kling-v3-omni, byteplus/dreamina-seedance-2-0-260128, minimax/minimax-h3
- TTS: openai/tts-1, openai/tts-1-hd
"""

import os
import sys
import requests
import io
import json
import time
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from abc import ABC, abstractmethod
from PIL import Image


class BaseEngine(ABC):
    """API 引擎基类"""
    
    @abstractmethod
    def generate_single(
        self,
        prompt: str,
        negative: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg: float = 7.5,
        seed: Optional[int] = None,
    ) -> Image.Image:
        """生成单张图片"""
        pass
    
    @abstractmethod
    def get_usage(self) -> Dict[str, Any]:
        """获取使用量信息"""
        pass
    
    def get_name(self) -> str:
        return self.__class__.__name__.replace('Engine', '')


class OrcaRouterEngine(BaseEngine):
    """
    OrcaRouter 多模态引擎
    
    OrcaRouter 是一个 OpenAI 兼容的 AI 网关，统一访问 200+ 模型：
    - OpenAI (GPT-5.2, GPT-4o, DALL-E 3, GPT-Image-1)
    - Anthropic (Claude Opus 5, Sonnet 4.6)
    - Google Gemini (Gemini 2.5 Pro/Flash)
    - DeepSeek (DeepSeek V4, R1)
    - xAI Grok
    - 阿里巴巴 Qwen
    - Moonshot Kimi
    - MiniMax
    - Z.ai
    - Kling (快手视频)
    - ByteDance Seedance (视频)
    """
    
    # 默认模型配置
    DEFAULT_MODELS = {
        "chat": "openai/gpt-4o-mini",
        "vision": "openai/gpt-4o",
        "reasoning": "anthropic/claude-opus-4.6",
        "image": "openai/gpt-image-1",
        "tts": "openai/tts-1",
        "video_kling": "kling/kling-v3-omni",
        "video_seedance": "byteplus/dreamina-seedance-2-0-260128",
        "video_minimax": "minimax/minimax-h3",
    }
    
    # API 路由
    ROUTES = ["https://api.orcarouter.ai/v1"]
    
    # 支持的 TTS 音频格式
    SUPPORTED_TTS_FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]
    
    # 支持的图像尺寸
    IMAGE_SIZES = ["256x256", "512x512", "1024x1024", "1024x1792", "1792x1024"]
    
    def __init__(
        self,
        api_key: str,
        base_url: str = None,
        model: str = None,
        chat_model: str = None,
        image_model: str = None,
        tts_model: str = None,
        video_model: str = None,
        vision_model: str = None,
        reasoning_model: str = None,
    ):
        """
        初始化 OrcaRouter 引擎
        
        Args:
            api_key: OrcaRouter API Key (以 sk-orca- 开头)
            base_url: API 地址（默认使用官方地址）
            model: 默认模型
            chat_model: 聊天模型
            image_model: 图像生成模型
            tts_model: 文本转语音模型
            video_model: 视频生成模型
            vision_model: 视觉理解模型
            reasoning_model: 深度推理模型
        """
        self.api_key = api_key
        
        if base_url:
            self.base_url = base_url.rstrip('/')
        else:
            self.base_url = self.ROUTES[0]
        
        self._failed_routes = set()
        
        # 各能力模型配置
        self.chat_model = chat_model or model or self.DEFAULT_MODELS["chat"]
        self.image_model = image_model or self.DEFAULT_MODELS["image"]
        self.tts_model = tts_model or self.DEFAULT_MODELS["tts"]
        self.video_model = video_model or self.DEFAULT_MODELS["video_kling"]
        self.vision_model = vision_model or model or self.DEFAULT_MODELS["vision"]
        self.reasoning_model = reasoning_model or self.DEFAULT_MODELS["reasoning"]
        
        self.last_request_time = 0
        self.min_interval = 0.5
        
        if not self.api_key:
            print("⚠️ 未设置 ORCAROUTER_API_KEY，请从 https://www.orcarouter.ai/ 注册获取")
        
        print(f"🔍 OrcaRouter 引擎初始化")
        print(f"🔍 API 地址: {self.base_url}")
        print(f"🔍 聊天模型: {self.chat_model}")
        print(f"🔍 图像模型: {self.image_model}")
        print(f"🔍 语音模型: {self.tts_model}")
        print(f"🔍 视频模型: {self.video_model}")
    
    # ==================== 核心请求方法 ====================
    
    def _request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        timeout: int = 120,
        stream: bool = False,
    ) -> Union[Dict[str, Any], requests.Response]:
        """发送请求到 OrcaRouter API"""
        if not self.api_key:
            raise ValueError("请设置 ORCAROUTER_API_KEY")
        
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                if stream:
                    response = requests.post(url, headers=headers, json=data, stream=True, timeout=timeout)
                    self.last_request_time = time.time()
                    return response
                
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
                self.last_request_time = time.time()
                
                if response.status_code == 429:
                    print(f"⚠️ 请求限流 (429)，等待后重试...")
                    time.sleep(3)
                    continue
                
                if response.status_code != 200:
                    error_detail = {}
                    try:
                        error_detail = response.json()
                    except:
                        pass
                    
                    if error_detail:
                        error_msg = error_detail.get('error', {}).get('message', str(error_detail))
                    else:
                        error_msg = response.text[:200]
                    
                    raise Exception(f"OrcaRouter API 调用失败 ({response.status_code}): {error_msg}")
                
                return response.json()
                
            except requests.exceptions.ConnectionError as e:
                if attempt == max_attempts - 1:
                    raise Exception(f"OrcaRouter 连接失败: {e}")
                time.sleep(2)
                continue
            except requests.exceptions.Timeout:
                if attempt == max_attempts - 1:
                    raise Exception(f"OrcaRouter 超时: {e}")
                time.sleep(2)
                continue
            except requests.exceptions.RequestException as e:
                if attempt == max_attempts - 1:
                    raise Exception(f"OrcaRouter 请求失败: {e}")
                time.sleep(2)
                continue
        
        raise Exception("OrcaRouter 所有尝试均失败")
    
    def _download_image(self, image_url: str) -> bytes:
        """下载图片"""
        img_response = requests.get(image_url, timeout=30)
        if img_response.status_code != 200:
            raise Exception(f"下载图片失败: {img_response.status_code}")
        return img_response.content
    
    # ==================== 1. Chat / 对话 ====================
    
    def chat(
        self,
        messages: List[Dict[str, Any]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        tools: List[Dict] = None,
        tool_choice: Union[str, Dict] = None,
        response_format: Dict = None,
        extra_body: Dict = None,
    ) -> str:
        """
        Chat 对话/推理
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            model: 模型名称（默认使用 chat_model）
            temperature: 温度参数
            max_tokens: 最大 token 数
            stream: 是否流式输出
            tools: 工具列表 [{"type": "function", "function": {...}}]
            tool_choice: 工具选择策略 ("auto", "none", "required")
            response_format: 结构化输出格式 {"type": "json_object"}
            extra_body: 额外参数
        
        Returns:
            模型响应文本
        """
        model = model or self.chat_model
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        
        if tools:
            data["tools"] = tools
        if tool_choice:
            data["tool_choice"] = tool_choice
        if response_format:
            data["response_format"] = response_format
        if extra_body:
            data.update(extra_body)
        
        print(f"🔍 OrcaRouter Chat")
        print(f"🔍 模型: {model}, 消息数: {len(messages)}")
        if tools:
            print(f"🔍 工具数量: {len(tools)}")
        
        if stream:
            response = self._request("chat/completions", data, stream=True)
            return self._parse_stream(response)
        
        result = self._request("chat/completions", data)
        
        if 'choices' in result and result['choices']:
            choice = result['choices'][0]
            message = choice.get('message', {})
            
            # 处理工具调用
            if message.get('tool_calls'):
                return message
            
            return message.get('content', '')
        
        raise Exception(f"无法解析推理结果: {json.dumps(result)[:300]}")
    
    def _parse_stream(self, response) -> str:
        """解析流式响应"""
        result_text = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    line = line[6:]
                    if line == '[DONE]':
                        break
                    try:
                        chunk = json.loads(line)
                        if 'choices' in chunk and chunk['choices']:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                print(content, end='', flush=True)
                                result_text += content
                    except:
                        pass
        print()
        return result_text
    
    def chat_simple(self, prompt: str, system_prompt: str = None, model: str = None, **kwargs) -> str:
        """简化版 Chat 对话"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages, model=model, **kwargs)
    
    def chat_vision(
        self,
        prompt: str,
        image_bytes: bytes = None,
        image_url: str = None,
        model: str = None,
        **kwargs
    ) -> str:
        """视觉理解对话（支持图片输入）"""
        model = model or self.vision_model
        
        content_parts = [{"type": "text", "text": prompt}]
        
        if image_bytes:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
            })
        elif image_url:
            content_parts.append({"type": "image_url", "image_url": {"url": image_url}})
        
        messages = [{"role": "user", "content": content_parts}]
        return self.chat(messages, model=model, **kwargs)
    
    def chat_tool_call(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict],
        model: str = None,
        **kwargs
    ) -> Dict:
        """执行工具调用"""
        model = model or self.chat_model
        return self.chat(
            messages=messages,
            model=model,
            tools=tools,
            tool_choice="auto",
            **kwargs
        )
    
    # ==================== 2. 图像生成（实现 BaseEngine） ====================
    
    def generate_single(
        self,
        prompt: str,
        negative: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg: float = 7.5,
        seed: int = None,
    ) -> Image.Image:
        """文生图 - 返回 PIL Image（兼容 BaseEngine 接口）"""
        size = f"{width}x{height}"
        
        data = {
            "model": self.image_model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "b64_json",
        }
        
        if seed is not None:
            data["seed"] = seed
        
        print(f"🔍 OrcaRouter 图像生成")
        print(f"🔍 模型: {self.image_model}, 尺寸: {size}")
        
        result = self._request("images/generations", data)
        
        if 'data' in result and result['data']:
            item = result['data'][0]
            
            # 优先使用 base64
            b64 = item.get('b64_json', '')
            if b64:
                if b64.startswith('data:image'):
                    b64 = b64.split(',', 1)[1]
                return Image.open(io.BytesIO(base64.b64decode(b64)))
            
            # 回退到 URL
            img_url = item.get('url')
            if img_url:
                return Image.open(io.BytesIO(self._download_image(img_url)))
        
        raise Exception(f"无法解析图片结果: {json.dumps(result)[:200]}")
    
    def generate_single(
        self,
        prompt: str,
        negative: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg: float = 7.5,
        seed: Optional[int] = None,
    ):
        """
        生成单张图片 - 兼容 BaseEngine 接口
        
        Args:
            prompt: 图像描述提示词
            negative: 负向提示词（暂不支持）
            width: 图像宽度
            height: 图像高度
            steps: 采样步数（暂不支持）
            cfg: CFG Scale（暂不支持）
            seed: 随机种子
        
        Returns:
            PIL.Image.Image 对象
        """
        from PIL import Image
        import io
        
        size = f"{width}x{height}"
        
        data = {
            "model": self.image_model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "b64_json",
        }
        
        if seed is not None:
            data["seed"] = seed
        
        print(f"🔍 OrcaRouter 图像生成 (generate_single)")
        print(f"🔍 模型: {self.image_model}, 尺寸: {size}")
        
        result = self._request("images/generations", data)
        
        if 'data' in result and result['data']:
            item = result['data'][0]
            
            # 优先使用 base64
            b64 = item.get('b64_json', '')
            if b64:
                if b64.startswith('data:image'):
                    b64 = b64.split(',', 1)[1]
                return Image.open(io.BytesIO(base64.b64decode(b64)))
            
            # 回退到 URL
            img_url = item.get('url')
            if img_url:
                return Image.open(io.BytesIO(self._download_image(img_url)))
        
        raise Exception(f"无法解析图片结果: {json.dumps(result)[:200]}")
    
    def generate_single(
        self,
        prompt: str,
        negative: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg: float = 7.5,
        seed: Optional[int] = None,
    ):
        """
        生成单张图片 - 兼容 BaseEngine 接口
        
        Args:
            prompt: 图像描述提示词
            negative: 负向提示词（暂不支持）
            width: 图像宽度
            height: 图像高度
            steps: 采样步数（暂不支持）
            cfg: CFG Scale（暂不支持）
            seed: 随机种子
        
        Returns:
            PIL.Image.Image 对象
        """
        from PIL import Image
        import io
        
        size = f"{width}x{height}"
        
        data = {
            "model": self.image_model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "b64_json",
        }
        
        if seed is not None:
            data["seed"] = seed
        
        print(f"🔍 OrcaRouter 图像生成 (generate_single)")
        print(f"🔍 模型: {self.image_model}, 尺寸: {size}")
        
        result = self._request("images/generations", data)
        
        if 'data' in result and result['data']:
            item = result['data'][0]
            
            # 优先使用 base64
            b64 = item.get('b64_json', '')
            if b64:
                if b64.startswith('data:image'):
                    b64 = b64.split(',', 1)[1]
                return Image.open(io.BytesIO(base64.b64decode(b64)))
            
            # 回退到 URL
            img_url = item.get('url')
            if img_url:
                return Image.open(io.BytesIO(self._download_image(img_url)))
        
        raise Exception(f"无法解析图片结果: {json.dumps(result)[:200]}")
    
    def generate_image(
        self,
        prompt: str,
        model: str = None,
        size: str = "1024x1024",
        n: int = 1,
        quality: str = "standard",
        style: str = "vivid",
        response_format: str = "url",
    ) -> List[Dict[str, Any]]:
        """
        图像生成 - 返回详细信息列表
        
        支持的模型：
        - openai/gpt-image-1 (多模态，支持编辑)
        - openai/dall-e-3 (高质量静态图)
        - google/imagen-4.0-standard-generate-001
        - xai/grok-imagine-image
        """
        model = model or self.image_model
        
        data = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
            "response_format": response_format,
        }
        
        if quality:
            data["quality"] = quality
        if style:
            data["style"] = style
        
        print(f"🔍 OrcaRouter 图像生成")
        print(f"🔍 模型: {model}, 尺寸: {size}, 数量: {n}")
        
        result = self._request("images/generations", data)
        
        images = []
        if 'data' in result:
            for item in result['data']:
                images.append({
                    "url": item.get('url'),
                    "revised_prompt": item.get('revised_prompt'),
                    "base64": item.get('b64_json'),
                })
        
        return images
    
    # ==================== 3. 文本转语音 ====================
    
    def text_to_speech(
        self,
        input_text: str,
        model: str = None,
        voice: str = "alloy",
        speed: float = 1.0,
        output_format: str = "mp3",
    ) -> bytes:
        """
        文本转语音
        
        Args:
            input_text: 要转换为语音的文本
            model: 语音合成模型（如 openai/tts-1, openai/tts-1-hd）
            voice: 声音类型（alloy, echo, fable, onyx, nova, shimmer）
            speed: 语速（0.25 - 4.0）
            output_format: 输出格式（mp3, opus, aac, flac, wav, pcm）
        
        Returns:
            音频字节数据
        """
        if output_format not in self.SUPPORTED_TTS_FORMATS:
            raise ValueError(f"不支持的输出格式: {output_format}，可选: {self.SUPPORTED_TTS_FORMATS}")
        
        model = model or self.tts_model
        
        data = {
            "model": model,
            "input": input_text,
            "voice": voice,
            "speed": speed,
            "response_format": output_format,
        }
        
        print(f"🔍 OrcaRouter 文本转语音")
        print(f"🔍 模型: {model}, 声音: {voice}, 语速: {speed}")
        
        result = self._request("audio/speech", data)
        
        # 处理不同类型的响应
        if isinstance(result, dict) and 'audio' in result:
            return result['audio']
        elif hasattr(result, 'content'):
            return result.content
        elif hasattr(result, 'body'):
            return result.body.read()
        
        raise Exception(f"无法解析语音结果: {str(result)[:200]}")
    
    def save_tts(
        self,
        input_text: str,
        filepath: str,
        model: str = None,
        voice: str = "alloy",
        speed: float = 1.0,
        output_format: str = "mp3",
    ) -> str:
        """文本转语音并保存到文件"""
        audio_data = self.text_to_speech(input_text, model, voice, speed, output_format)
        
        with open(filepath, 'wb') as f:
            f.write(audio_data)
        
        print(f"✅ 语音已保存至: {filepath}")
        return filepath
    
    # ==================== 4. 视频生成 ====================
    
    def video_generation(
        self,
        prompt: str,
        model: str = None,
        image: bytes = None,
        image_url: str = None,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        resolution: str = "720p",
        mode: str = "text-to-video",
        callback_url: str = None,
        # Kling 特有参数
        sound: str = None,
        multi_shot: bool = False,
        # Seedance 特有参数
        generate_audio: bool = True,
        watermark: bool = False,
        seed: int = None,
        service_tier: str = None,
        # MiniMax 特有参数
        first_frame_image: bytes = None,
        last_frame_image: bytes = None,
    ) -> Dict[str, Any]:
        """
        视频生成（异步）
        
        支持的模型：
        - kling/kling-v3-omni (Omni 多镜头)
        - kling/kling-v2-6 (运动+音频控制)
        - byteplus/dreamina-seedance-2-0-260128 (多模态参考)
        - minimax/minimax-h3 (原生立体音频)
        
        Returns:
            包含 task_id 的任务信息
        """
        model = model or self.video_model
        prefix = model.split('/')[0] if '/' in model else "kling"
        
        data: Dict[str, Any] = {"model": model, "prompt": prompt}
        
        if prefix == "kling":
            data["metadata"] = {
                "mode": mode,
                "aspect_ratio": aspect_ratio,
                "duration": duration,
                "resolution": resolution,
            }
            if image_url:
                data["image"] = image_url
            elif image:
                data["image"] = f"data:image/png;base64,{base64.b64encode(image).decode('utf-8')}"
            if sound:
                data["metadata"]["sound"] = sound
            if multi_shot:
                data["metadata"]["multi_shot"] = True
        elif prefix == "byteplus":
            data["metadata"] = {
                "content": [{"type": "text", "text": prompt}],
                "ratio": aspect_ratio,
                "duration": duration,
                "generate_audio": generate_audio,
                "watermark": watermark,
                "resolution": resolution,
            }
            if seed is not None:
                data["metadata"]["seed"] = seed
            if service_tier:
                data["metadata"]["service_tier"] = service_tier
        elif prefix == "minimax":
            data.update({"duration": duration, "size": resolution})
            if image_url:
                data["image"] = image_url
            elif image:
                data["images"] = [f"data:image/png;base64,{base64.b64encode(image).decode('utf-8')}"]
            if first_frame_image:
                data["first_frame_image"] = f"data:image/png;base64,{base64.b64encode(first_frame_image).decode('utf-8')}"
            if last_frame_image:
                data["last_frame_image"] = f"data:image/png;base64,{base64.b64encode(last_frame_image).decode('utf-8')}"
        
        if callback_url:
            data["callback_url"] = callback_url
        
        print(f"🔍 OrcaRouter 视频生成")
        print(f"🔍 模型: {model}, Provider: {prefix}")
        print(f"🔍 模式: {mode}, 时长: {duration}s")
        
        result = self._request("video/generations", data, timeout=300)
        return result
    
    def video_status(self, video_id: str, model: str = None) -> Dict[str, Any]:
        """查询视频生成状态"""
        model = model or self.video_model
        
        url = f"{self.base_url}/video/generations/{video_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        max_retries = 6
        wait = 15
        for attempt in range(max_retries):
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            
            if response.status_code == 429:
                print(f"⚠️ 状态查询被限流 (429)，{wait}s 后重试...")
                time.sleep(wait)
                wait = min(wait * 2, 90)
                continue
            
            raise Exception(f"查询视频状态失败 (HTTP {response.status_code}): {response.text[:200]}")
        
        raise Exception(f"状态查询连续 {max_retries} 次被限流，放弃")
    
    def wait_for_video(
        self,
        video_id: str,
        max_wait: int = 600,
        poll_interval: int = 10,
        model: str = None,
    ) -> str:
        """等待视频生成完成"""
        start_time = time.time()
        consecutive_fail = 0
        backoff = 15
        
        while time.time() - start_time < max_wait:
            try:
                status = self.video_status(video_id, model=model)
                consecutive_fail = 0
                backoff = 15
            except Exception as e:
                consecutive_fail += 1
                print(f"⚠️ 状态查询失败 ({consecutive_fail}): {str(e)[:120]}")
                if consecutive_fail >= 5:
                    raise Exception(f"状态查询连续失败 {consecutive_fail} 次，放弃")
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
                continue
            
            state = status.get('status', '')
            progress = status.get('progress', 0)
            print(f"📊 状态: {state}, 进度: {progress}%")
            
            if state == 'completed':
                url = status.get('video_url', status.get('url', ''))
                if url:
                    return url
                time.sleep(poll_interval)
                continue
            
            if state in ('failed', 'error'):
                error = status.get('error', '未知错误')
                raise Exception(f"视频生成失败: {error}")
            
            # 动态轮询间隔
            if progress and progress >= 90:
                time.sleep(max(5, poll_interval // 2))
            else:
                time.sleep(poll_interval)
        
        raise Exception(f"视频生成超时 ({max_wait}s)")
    
    # ==================== 5. Seedance 资产管理 ====================
    
    def list_asset_groups(
        self,
        group_type: str = "real_human",
        page_size: int = 20,
        cursor: str = None,
    ) -> Dict[str, Any]:
        """
        列出 Seedance 资产组
        
        Args:
            group_type: 资产类型（real_human, virtual_human, product, outfit, face, voice）
            page_size: 每页数量
            cursor: 分页游标
        
        Returns:
            资产组列表及分页信息
        """
        url = f"{self.base_url}/asset/groups"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        params = {"group_type": group_type, "page_size": page_size}
        if cursor:
            params["cursor"] = cursor
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"获取资产列表失败: {response.text[:200]}")
        
        return response.json()
    
    # ==================== 工具方法 ====================
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        获取可用模型列表
        
        Returns:
            模型列表
        """
        url = f"{self.base_url}/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            raise Exception(f"获取模型列表失败: {response.text[:200]}")
        
        return response.json().get('data', [])
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """获取单个模型详细信息"""
        url = f"{self.base_url}/models/{model_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            raise Exception(f"获取模型信息失败: {response.text[:200]}")
        
        return response.json()
    
    def get_usage(self) -> Dict[str, Any]:
        """获取使用量信息"""
        url = f"{self.base_url}/dashboard/billing/usage"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return {"info": "请登录 https://www.orcarouter.ai/dashboard 查看使用量"}
        
        return response.json()
    
    def get_name(self) -> str:
        return f"OrcaRouter (聊天: {self.chat_model}, 图像: {self.image_model})"
    
    def get_model(self) -> str:
        return self.chat_model


# ==================== 便捷函数 ====================

def create_orcarouter_engine(api_key: str, **kwargs) -> OrcaRouterEngine:
    """创建 OrcaRouter 引擎实例"""
    return OrcaRouterEngine(api_key=api_key, **kwargs)


def orca_chat(
    messages: List[Dict[str, Any]],
    api_key: str,
    model: str = None,
    **kwargs
) -> str:
    """便捷函数：执行 OrcaRouter Chat"""
    engine = OrcaRouterEngine(api_key=api_key)
    return engine.chat(messages, model=model, **kwargs)


def orca_image(
    prompt: str,
    api_key: str,
    model: str = None,
    size: str = "1024x1024",
    **kwargs
) -> List[Dict[str, Any]]:
    """便捷函数：生成图像"""
    engine = OrcaRouterEngine(api_key=api_key)
    return engine.generate_image(prompt, model=model, size=size, **kwargs)
