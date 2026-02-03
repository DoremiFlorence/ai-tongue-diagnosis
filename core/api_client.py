"""SiliconFlow API 客户端模块。"""

from typing import Any, Optional
import requests

from config.settings import (
    SILICONFLOW_API_KEY,
    CHAT_COMPLETIONS_ENDPOINT,
    VISION_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
)


class SiliconFlowClient:
    """SiliconFlow API 客户端。"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化客户端。

        Args:
            api_key: API 密钥，如未提供则从环境变量读取
        """
        self.api_key = api_key or SILICONFLOW_API_KEY
        if not self.api_key:
            raise ValueError("未配置 SILICONFLOW_API_KEY")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat_with_vision(
        self,
        text_prompt: str,
        image_base64: str,
        system_prompt: Optional[str] = None,
        history: Optional[list[dict[str, Any]]] = None,
        model: str = VISION_MODEL,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE,
    ) -> str:
        """发送带图片的对话请求。

        Args:
            text_prompt: 用户文本提示
            image_base64: 图片的 base64 编码
            system_prompt: 系统提示词
            history: 对话历史
            model: 使用的模型
            max_tokens: 最大生成 token 数
            temperature: 采样温度

        Returns:
            模型响应文本

        Raises:
            requests.RequestException: API 请求失败
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if history:
            messages.extend(history)

        user_content = [
            {"type": "text", "text": text_prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}",
                    "detail": "high",
                },
            },
        ]
        messages.append({"role": "user", "content": user_content})

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        response = requests.post(
            CHAT_COMPLETIONS_ENDPOINT,
            json=payload,
            headers=self.headers,
            timeout=120,
        )
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def chat(
        self,
        messages: list[dict[str, Any]],
        model: str = VISION_MODEL,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE,
    ) -> str:
        """发送纯文本对话请求。

        Args:
            messages: 对话消息列表
            model: 使用的模型
            max_tokens: 最大生成 token 数
            temperature: 采样温度

        Returns:
            模型响应文本
        """
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        response = requests.post(
            CHAT_COMPLETIONS_ENDPOINT,
            json=payload,
            headers=self.headers,
            timeout=120,
        )
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]
