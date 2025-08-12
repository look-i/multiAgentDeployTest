# API请求响应模型
# API Request/Response Schemas

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

# 基础响应模型
class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(description="请求是否成功")
    message: str = Field(description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")

class DataResponse(BaseResponse):
    """数据响应模型"""
    data: Optional[Any] = Field(default=None, description="响应数据")

# 学习风格模型
class LearningStyleData(BaseModel):
    """学习风格数据"""
    visual: float = Field(ge=0, le=1, description="视觉学习偏好")
    auditory: float = Field(ge=0, le=1, description="听觉学习偏好")
    reading: float = Field(ge=0, le=1, description="阅读学习偏好")
    kinesthetic: float = Field(ge=0, le=1, description="动觉学习偏好")

# 认知状态模型
class CognitiveState(BaseModel):
    """认知状态数据"""
    cognitive_load: float = Field(ge=0, le=1, description="认知负荷水平")
    attention_level: float = Field(ge=0, le=1, description="注意力水平")
    comprehension_rate: float = Field(ge=0, le=1, description="理解率")
    learning_progress: float = Field(ge=0, le=1, description="学习进度")

# 学习上下文模型
class LearningContext(BaseModel):
    """学习上下文数据"""
    user_id: str = Field(description="用户ID")
    session_id: str = Field(description="会话ID")
    learning_style: LearningStyleData = Field(description="学习风格")
    cognitive_state: CognitiveState = Field(description="认知状态")
    current_topic: Optional[str] = Field(default=None, description="当前学习主题")
    difficulty_level: Optional[int] = Field(default=1, ge=1, le=5, description="难度等级")
    learning_history: Optional[List[str]] = Field(default=[], description="学习历史")

# 智能体对话请求
class AgentChatRequest(BaseModel):
    """智能体对话请求"""
    message: str = Field(description="用户消息")
    agent_type: str = Field(description="智能体类型 (expert/assistant/peer)")
    context: Optional[LearningContext] = Field(default=None, description="学习上下文")

# 智能体对话响应
class AgentChatResponse(DataResponse):
    """智能体对话响应"""
    agent_type: str = Field(description="智能体类型")
    response: str = Field(description="智能体回复")
    suggestions: Optional[List[str]] = Field(default=[], description="学习建议")

# 个性化内容请求
class PersonalizedContentRequest(BaseModel):
    """个性化内容请求"""
    topic: str = Field(description="学习主题")
    content_type: str = Field(description="内容类型 (explanation/exercise/example)")
    context: LearningContext = Field(description="学习上下文")

# 个性化内容响应
class PersonalizedContentResponse(DataResponse):
    """个性化内容响应"""
    content: str = Field(description="个性化内容")
    content_type: str = Field(description="内容类型")
    difficulty_level: int = Field(description="内容难度等级")
    learning_style_match: Dict[str, float] = Field(description="学习风格匹配度")

# 学习路径请求
class LearningPathRequest(BaseModel):
    """学习路径请求"""
    subject: str = Field(description="学科")
    target_skills: List[str] = Field(description="目标技能")
    context: LearningContext = Field(description="学习上下文")

# 学习路径响应
class LearningPathResponse(DataResponse):
    """学习路径响应"""
    path_id: str = Field(description="路径ID")
    steps: List[Dict[str, Any]] = Field(description="学习步骤")
    estimated_duration: int = Field(description="预估学习时长(分钟)")
    difficulty_progression: List[int] = Field(description="难度递进")

# 深度学习模式请求
class DeepLearningRequest(BaseModel):
    """深度学习模式请求"""
    topic: str = Field(description="学习主题")
    learning_goal: str = Field(description="学习目标")
    context: LearningContext = Field(description="学习上下文")

# 深度学习模式响应
class DeepLearningResponse(DataResponse):
    """深度学习模式响应"""
    learning_plan: Dict[str, Any] = Field(description="深度学习计划")
    key_concepts: List[str] = Field(description="核心概念")
    practice_exercises: List[Dict[str, Any]] = Field(description="练习题")
    assessment_criteria: List[str] = Field(description="评估标准")

# 学习分析请求
class LearningAnalyticsRequest(BaseModel):
    """学习分析请求"""
    user_id: str = Field(description="用户ID")
    time_range: Optional[Dict[str, str]] = Field(default=None, description="时间范围")
    analysis_type: str = Field(description="分析类型 (progress/performance/behavior)")

# 学习分析响应
class LearningAnalyticsResponse(DataResponse):
    """学习分析响应"""
    analysis_type: str = Field(description="分析类型")
    metrics: Dict[str, Any] = Field(description="分析指标")
    insights: List[str] = Field(description="学习洞察")
    recommendations: List[str] = Field(description="改进建议")

# 智能问答请求
class QARequest(BaseModel):
    """智能问答请求"""
    question: str = Field(description="问题")
    subject: Optional[str] = Field(default=None, description="学科领域")
    context: Optional[LearningContext] = Field(default=None, description="学习上下文")

# 智能问答响应
class QAResponse(DataResponse):
    """智能问答响应"""
    answer: str = Field(description="答案")
    confidence: float = Field(ge=0, le=1, description="置信度")
    related_topics: List[str] = Field(description="相关主题")
    follow_up_questions: List[str] = Field(description="后续问题建议")

# 系统健康检查响应
class HealthCheckResponse(BaseResponse):
    """系统健康检查响应"""
    version: str = Field(description="系统版本")
    status: str = Field(description="系统状态")
    components: Dict[str, str] = Field(description="组件状态")


# --- 多智能体协作聊天模型 ---

class Message(BaseModel):
    """单条聊天消息模型"""
    role: str = Field(description="消息发送者的角色 (e.g., 'user', 'ExpertAgent')")
    content: str = Field(description="消息内容")

class ChatSession(BaseModel):
    """聊天会话状态模型（用于无状态传递）"""
    participants: List[str] = Field(description="参与会话的智能体名称列表")
    history: List[Message] = Field(description="聊天历史记录")
    session_id: Optional[str] = Field(default=None, description="可选的会话ID")

class ChatSessionInitResponse(BaseResponse):
    """聊天会话初始化响应"""
    session_id: str = Field(description="本次会话的唯一标识符")
    initial_history: List[Dict[str, Any]] = Field(description="包含开场白的初始对话历史")
    opening_remarks: List[Dict[str, Any]] = Field(description="各智能体的开场白")

class CollaborateRequest(BaseModel):
    """协作聊天请求"""
    session_id: str = Field(description="当前会话的唯一标识符")
    history: List[Message] = Field(description="到目前为止的完整对话历史")
    user_message: Message = Field(description="用户的最新消息")

class CollaborateResponse(BaseResponse):
    """协作聊天响应"""
    agent_responses: List[Dict[str, Any]] = Field(description="一个或多个智能体的响应")
    updated_history: List[Dict[str, Any]] = Field(description="包含新响应的完整对话历史")