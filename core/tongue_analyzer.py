"""舌诊分析器模块。"""

from typing import Optional

from core.api_client import SiliconFlowClient
from prompts.system_prompts import (
    TONGUE_DIAGNOSIS_SYSTEM_PROMPT,
    INITIAL_ANALYSIS_PROMPT,
)


class TongueAnalyzer:
    """舌诊分析器。"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化分析器。

        Args:
            api_key: API 密钥
        """
        self.client = SiliconFlowClient(api_key)

    def analyze_tongue_image(self, image_base64: str) -> str:
        """分析舌苔图片。

        Args:
            image_base64: 图片的 base64 编码

        Returns:
            分析结果文本
        """
        return self.client.chat_with_vision(
            text_prompt=INITIAL_ANALYSIS_PROMPT,
            image_base64=image_base64,
            system_prompt=TONGUE_DIAGNOSIS_SYSTEM_PROMPT,
        )
