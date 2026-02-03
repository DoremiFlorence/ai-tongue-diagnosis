"""多轮问诊引擎模块。"""

from typing import Any, Optional

from core.api_client import SiliconFlowClient
from prompts.system_prompts import TONGUE_DIAGNOSIS_SYSTEM_PROMPT


class DiagnosisEngine:
    """多轮问诊引擎。"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化引擎。

        Args:
            api_key: API 密钥
        """
        self.client = SiliconFlowClient(api_key)

    def continue_conversation(
        self,
        user_message: str,
        conversation_history: list[dict[str, Any]],
        initial_analysis: Optional[str] = None,
    ) -> str:
        """继续对话。

        Args:
            user_message: 用户消息
            conversation_history: 对话历史
            initial_analysis: 初始舌诊分析结果

        Returns:
            AI 回复
        """
        messages = [{"role": "system", "content": TONGUE_DIAGNOSIS_SYSTEM_PROMPT}]

        if initial_analysis and not conversation_history:
            messages.append({
                "role": "assistant",
                "content": initial_analysis,
            })

        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        return self.client.chat(messages)

    def generate_final_diagnosis(
        self,
        conversation_history: list[dict[str, Any]],
        initial_analysis: str,
    ) -> str:
        """生成最终诊断报告。

        Args:
            conversation_history: 完整对话历史
            initial_analysis: 初始舌诊分析

        Returns:
            最终诊断报告
        """
        prompt = """基于以上所有的舌诊分析和问诊对话，请生成一份完整的诊断报告，包括：

## 一、舌诊总结
简要总结舌象特征

## 二、综合辨证
根据舌诊和问诊信息，给出综合辨证分析

## 三、体质判断
判断患者的中医体质类型

## 四、健康评估
当前健康状态评估

## 五、调理建议

### 1. 饮食调理
- 宜吃：
- 忌吃：
- 推荐食谱：

### 2. 作息建议
- 睡眠：
- 运动：

### 3. 穴位保健
推荐的保健穴位及按摩方法

### 4. 注意事项
需要特别注意的健康问题

## 六、就医建议
是否需要进一步就医检查"""

        messages = [{"role": "system", "content": TONGUE_DIAGNOSIS_SYSTEM_PROMPT}]
        messages.append({"role": "assistant", "content": initial_analysis})
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": prompt})

        return self.client.chat(messages)
