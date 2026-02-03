"""Pydantic 数据模型模块。"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TongueAnalysisSchema(BaseModel):
    """舌诊分析结果模型。"""

    tongue_color: str = Field(description="舌质颜色")
    tongue_shape: str = Field(description="舌形特征")
    coating_color: str = Field(description="舌苔颜色")
    coating_thickness: str = Field(description="舌苔厚薄")
    coating_texture: str = Field(description="舌苔质地")
    raw_analysis: str = Field(description="完整分析文本")


class DiagnosisResultSchema(BaseModel):
    """诊断结果模型。"""

    syndrome_type: str = Field(description="证型判断")
    constitution_type: str = Field(description="体质类型")
    health_issues: list[str] = Field(default_factory=list, description="健康问题列表")
    recommendations: list[str] = Field(default_factory=list, description="调理建议列表")


class SessionSchema(BaseModel):
    """诊断会话模型。"""

    session_id: str = Field(description="会话ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    image_path: Optional[str] = Field(default=None, description="舌苔图片路径")
    initial_analysis: Optional[str] = Field(default=None, description="初始舌诊分析")
    conversation_history: list[dict] = Field(default_factory=list, description="对话历史")
    final_diagnosis: Optional[str] = Field(default=None, description="最终诊断")
    recommendations: Optional[str] = Field(default=None, description="调理建议")


class MessageSchema(BaseModel):
    """对话消息模型。"""

    role: str = Field(description="角色: user/assistant")
    content: str = Field(description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
