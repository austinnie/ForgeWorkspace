# core/api_engines/tokenworks.py
"""
TokenWorks（硅碳相变）引擎 —— 中国大陆直连，OpenAI 兼容协议

⚠️ 通道现状（2026-09-30 实测，写代码时请以此为准）：
   ✅ 文本 / 推理 / 长上下文 —— 20 个模型实测可调（见 DEFAULT_MODELS）
   ⛔ 文生图 / 视频 —— 我们的图像与视频通道尚未接入，实测
      /v1/images/generations 返回 not implemented、视频模型返回
      model_not_found。ArtForge 的「题词生成」可以直接用文本接口；
      图像生成建议继续走 Agnes / Pollinations。

与 ArtForge 其他 api_engines 的接口保持一致：
    TokenWorksEngine(api_key=..., text_model=..., image_model=..., video_model=...)
    .chat(prompt)        -> str
    .text_to_image(prompt, size=...) -> bytes
    .video(prompt, ...)  -> 任务结果

实测环境：Python 3.10+，requests
"""
import base64
import json
import time
from enum import Enum
from typing import Any, Dict, List, Optional

import requests

BASE_URL = "https://api.token8341.com/v1"   # 生产端点（OpenAI 兼容）


class TokenWorksMode(Enum):
    CHAT = "chat"
    TEXT_TO_IMAGE = "text-to-image"
    VIDEO = "video"


class TokenWorksEngine:
    """TokenWorks 多模态引擎（OpenAI 兼容：一个 key 调全部模型）"""

    # 按用途分类的可用模型（2026-09-30 线上实查，共 36 个）
    DEFAULT_MODELS = {
        "chat": "deepseek-v4-pro",          # 旗舰通用，¥7.2/¥21.6 每百万 token
        "chat_fast": "deepseek-v4-flash",   # 快而便宜，¥1.6/¥3.2
        "chat_long": "qwen3.8-max",         # 长上下文
        "chat_reason": "kimi-k3",           # 旗舰推理
        "text-to-image": "qwen-image-2.1",
        "video": "wan2.2-t2v-a14b",
    }

    def __init__(
        self,
        api_key: str,
        base_url: str = None,
        model: str = None,
        image_model: str = None,
        text_model: str = None,
        video_model: str = None,
        vision_model: str = None,
    ):
        self.api_key = api_key
        self.base_url = (base_url or BASE_URL).rstrip("/")
        self.text_model = text_model or model or self.DEFAULT_MODELS["chat"]
        self.image_model = image_model or self.DEFAULT_MODELS["text-to-image"]
        self.video_model = video_model or self.DEFAULT_MODELS["video"]
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    # ---------- 基础 ----------
    def _post(self, path: str, payload: Dict[str, Any], timeout: int = 120) -> Dict[str, Any]:
        r = self.session.post(f"{self.base_url}{path}", json=payload, timeout=timeout)
        if r.status_code != 200:
            raise RuntimeError(f"TokenWorks 返回 {r.status_code}: {r.text[:300]}")
        return r.json()

    def list_models(self) -> List[str]:
        """列出当前可调用的模型名（无需 key 也能查 /api/pricing）"""
        r = requests.get("https://api.token8341.com/api/pricing", timeout=30)
        return sorted({m["model_name"] for m in r.json().get("data", [])})

    # ---------- 文本 ----------
    def chat(self, prompt: str, system: str = None, model: str = None,
             temperature: float = 0.8, max_tokens: int = 4096) -> str:
        """文本推理（题词 / 汉诗 / 和歌 / 俳句 生成都走这里）"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        data = self._post("/chat/completions", {
            "model": model or self.text_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        })
        msg = data["choices"][0]["message"]
        text = (msg.get("content") or "").strip()
        if text:
            return text
        # 有些模型先输出思维链，max_tokens 太小会只拿到 reasoning_content。
        # 这里放大预算再试一次，避免把思维链当正文用。
        if msg.get("reasoning_content"):
            retry = self._post("/chat/completions", {
                "model": model or self.text_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": min(max_tokens * 4, 16384),
            })
            m2 = retry["choices"][0]["message"]
            return (m2.get("content") or "").strip()
        return ""

    def chat_stream(self, prompt: str, model: str = None, **kw):
        """流式输出（长文生成用，避免超时）"""
        payload = {"model": model or self.text_model,
                   "messages": [{"role": "user", "content": prompt}], "stream": True}
        payload.update(kw)
        with self.session.post(f"{self.base_url}/chat/completions", json=payload,
                               stream=True, timeout=300) as r:
            for line in r.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                body = line[5:].strip()
                if body == "[DONE]":
                    break
                try:
                    delta = json.loads(body)["choices"][0].get("delta", {})
                except Exception:
                    continue
                piece = delta.get("content") or ""
                if piece:
                    yield piece

    # ---------- 图像 ----------
    def text_to_image(self, prompt: str, size: str = "1024x1024",
                      model: str = None, save_to: str = None) -> bytes:
        """文生图。返回 PNG 字节；给了 save_to 就同时落盘。"""
        data = self._post("/images/generations", {
            "model": model or self.image_model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "b64_json",
        }, timeout=300)
        item = data["data"][0]
        raw = base64.b64decode(item["b64_json"]) if item.get("b64_json") \
            else requests.get(item["url"], timeout=120).content
        if save_to:
            with open(save_to, "wb") as f:
                f.write(raw)
        return raw

    # ---------- 视频 ----------
    def video(self, prompt: str, model: str = None, wait: int = 600) -> Dict[str, Any]:
        """视频生成（同步端点，内部轮询到完成为止）"""
        return self._post("/video/generations", {
            "model": model or self.video_model,
            "prompt": prompt,
        }, timeout=wait)


if __name__ == "__main__":
    import os
    eng = TokenWorksEngine(api_key=os.environ["TOKENWORKS_KEY"])
    print("可用模型数:", len(eng.list_models()))
    print("题词示例:", eng.chat("为浮世绘《月下天狗》写一句 7 字汉诗题词，只回诗句，不要解释。",
                                model="deepseek-v4-flash", max_tokens=64))
