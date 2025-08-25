# API路由定义
# API Routes Definition

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any

from app.models.schemas import (
    AgentChatRequest, AgentChatResponse,
    PersonalizedContentRequest, PersonalizedContentResponse,
    LearningPathRequest, LearningPathResponse,
    DeepLearningRequest, DeepLearningResponse,
    LearningAnalyticsRequest, LearningAnalyticsResponse,
    QARequest, QAResponse,
    HealthCheckResponse,
    ChatSessionInitResponse, # 新增
    CollaborateRequest,      # 新增
    CollaborateResponse,     # 新增
    Message                  # 新增
)
from app.core.agent_manager import AgentManager
from app.core.chat_manager import ChatManager # 新增
from app.services.personalization_service import get_personalization_service
from app.services.deep_learning_service import get_deep_learning_service
from app.services.analytics_service import get_analytics_service
from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger("app.api")

# 创建API路由器
router = APIRouter(prefix=settings.api_prefix)

# 依赖注入函数：从app.state获取已初始化的AgentManager实例
def get_agent_manager_from_state(request: Request) -> AgentManager:
    """
    从FastAPI应用状态中获取已初始化的AgentManager实例
    
    这确保我们使用的是在应用启动时正确初始化的智能体管理器，
    而不是未初始化的全局单例实例。
    """
    return request.app.state.agent_manager

# 新增：用于ChatManager的依赖注入
def get_chat_manager(request: Request) -> ChatManager:
    """
    从FastAPI应用状态中获取ChatManager实例。
    """
    if not hasattr(request.app.state, 'chat_manager'):
        # 如果chat_manager还未初始化，则现在初始化它
        # 这需要AgentManager已经存在
        agent_manager = get_agent_manager_from_state(request)
        request.app.state.chat_manager = ChatManager(agent_manager)
    return request.app.state.chat_manager

@router.post("/agent/chat", response_model=AgentChatResponse)
async def agent_chat(
    request: AgentChatRequest,
    agent_manager = Depends(get_agent_manager_from_state)
):
    """
    智能体对话接口
    
    支持与专家、助教、同伴三类智能体进行对话交流。
    根据学习上下文提供个性化的智能回复。
    """
    try:
        logger.info(f"智能体对话请求: {request.agent_type} - {request.message[:50]}...")
        
        # 验证智能体类型
        valid_agents = ["expert", "assistant", "peer"]
        if request.agent_type not in valid_agents:
            raise HTTPException(
                status_code=400,
                detail=f"无效的智能体类型。支持的类型: {', '.join(valid_agents)}"
            )
        
        # 调用智能体进行对话
        context_dict = request.context.dict() if request.context else None
        response_text = await agent_manager.chat_with_agent(
            agent_type=request.agent_type,
            message=request.message,
            context=context_dict
        )
        
        # 生成学习建议（基于智能体类型）
        suggestions = _generate_suggestions(request.agent_type, request.message, response_text)
        
        return AgentChatResponse(
            success=True,
            message="对话成功",
            agent_type=request.agent_type,
            response=response_text,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"智能体对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")

@router.post("/content/personalized", response_model=PersonalizedContentResponse)
async def generate_personalized_content(
    request: PersonalizedContentRequest,
    personalization_service = Depends(get_personalization_service)
):
    """
    个性化内容生成接口
    
    根据学习者的学习风格和认知状态，生成个性化的学习内容。
    支持解释、练习、示例等多种内容类型。
    """
    try:
        logger.info(f"个性化内容生成: {request.topic} - {request.content_type}")
        
        # 验证内容类型
        valid_types = ["explanation", "exercise", "example"]
        if request.content_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"无效的内容类型。支持的类型: {', '.join(valid_types)}"
            )
        
        # 生成个性化内容
        result = await personalization_service.generate_personalized_content(request)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"个性化内容生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"内容生成失败: {str(e)}")

@router.post("/learning/path", response_model=LearningPathResponse)
async def generate_learning_path(
    request: LearningPathRequest,
    personalization_service = Depends(get_personalization_service)
):
    """
    个性化学习路径生成接口
    
    基于学习者特征和目标技能，生成个性化的学习路径。
    包含学习步骤、时长估算和难度递进安排。
    """
    try:
        logger.info(f"学习路径生成: {request.subject} - {len(request.target_skills)}个技能")
        
        # 验证目标技能
        if not request.target_skills:
            raise HTTPException(status_code=400, detail="目标技能列表不能为空")
        
        if len(request.target_skills) > 10:
            raise HTTPException(status_code=400, detail="目标技能数量不能超过10个")
        
        # 生成学习路径
        result = await personalization_service.generate_learning_path(request)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"学习路径生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"路径生成失败: {str(e)}")

# 移除旧的深度学习接口
# @router.post("/learning/deep-mode", response_model=DeepLearningResponse)
# async def create_deep_learning_plan(
#     request: DeepLearningRequest,
#     deep_learning_service = Depends(get_deep_learning_service)
# ):
#     """
#     深度学习模式接口
    
#     为复杂学习目标创建深度学习计划。
#     包含多阶段学习安排、核心概念提取、练习设计和评估标准。
#     """
#     try:
#         logger.info(f"深度学习计划创建: {request.topic} - {request.learning_goal}")
        
#         # 验证学习目标
#         if len(request.learning_goal.strip()) < 10:
#             raise HTTPException(status_code=400, detail="学习目标描述过于简短，请提供更详细的目标")
        
#         # 创建深度学习计划
#         result = await deep_learning_service.create_deep_learning_plan(request)
        
#         if not result.success:
#             raise HTTPException(status_code=500, detail=result.message)
        
#         return result
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"深度学习计划创建失败: {e}")
#         raise HTTPException(status_code=500, detail=f"计划创建失败: {str(e)}")

# --- 新增深度学习模式（多智能体协作）API ---

@router.post("/chat/session/init", response_model=ChatSessionInitResponse)
async def init_chat_session(
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    初始化深度学习模式的多智能体聊天会话。

    启动一个由专家、助教、同伴智能体组成的聊天室，
    并返回它们的开场白作为会话的开始。
    """
    try:
        logger.info("初始化新的深度学习聊天会话...")
        session_id, session, opening_remarks = await chat_manager.init_session()
        
        # 无状态：我们将初始历史和会话ID返回给客户端，由客户端负责维护
        initial_history = [msg.dict() for msg in session.history]

        return ChatSessionInitResponse(
            success=True,
            message="会话初始化成功",
            session_id=session_id,
            initial_history=initial_history,
            opening_remarks=opening_remarks
        )
    except Exception as e:
        logger.error(f"初始化聊天会话失败: {e}")
        raise HTTPException(status_code=500, detail=f"初始化会话失败: {str(e)}")


@router.post("/chat/collaborate", response_model=CollaborateResponse)
async def collaborate_chat(
    request: CollaborateRequest,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    在深度学习模式下进行协作式聊天。

    用户发送消息，系统根据对话历史和用户输入，
    动态选择最合适的智能体进行回应。
    """
    try:
        # 健壮日志：兼容可选的 user_message
        preview = None
        if request.user_message and isinstance(request.user_message.content, str):
            preview = request.user_message.content[:50]
        else:
            # 从history中反向查找最近一条用户消息用于日志预览
            for msg in reversed(request.history or []):
                if isinstance(msg.role, str) and msg.role.strip().lower() == "user":
                    preview = (msg.content or "")[:50]
                    break
        logger.info(f"处理协作聊天消息: {preview if preview else '无用户显式输入，基于历史继续协作'}...")

        # 轻度校验：history与user_message均缺失时，无法推进协作
        if (not request.history or len(request.history) == 0) and not request.user_message:
            raise HTTPException(status_code=422, detail="缺少对话历史及用户消息，请先调用 /chat/session/init 或提供 user_message")

        # 构建完整的对话历史（兼容可选user_message）
        full_history = list(request.history or [])
        if request.user_message:
            full_history = full_history + [request.user_message]
        
        # 将Pydantic模型转换为字典列表
        history_dicts = [msg.dict() for msg in full_history]

        # 调用ChatManager的collaborate方法处理消息（透传auto_config）
        agent_responses = await chat_manager.collaborate(
            session_id=request.session_id, 
            conversation_history=history_dicts,
            auto_config=request.auto_config  # 透传自动多轮配置
        )

        # 将智能体响应添加到历史记录中
        updated_history = full_history + [Message(**resp) for resp in agent_responses]

        return CollaborateResponse(
            success=True,
            message="协作响应成功",
            agent_responses=agent_responses,
            updated_history=[msg.dict() for msg in updated_history]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"协作聊天失败: {e}")
        raise HTTPException(status_code=500, detail=f"协作聊天失败: {str(e)}")


@router.post("/analytics/learning", response_model=LearningAnalyticsResponse)
async def analyze_learning_data(
    request: LearningAnalyticsRequest,
    analytics_service = Depends(get_analytics_service)
):
    """
    学习分析接口
    
    分析学习者的学习数据，提供进度、表现、行为等多维度分析。
    生成学习洞察和改进建议。
    """
    try:
        logger.info(f"学习分析: {request.user_id} - {request.analysis_type}")
        
        # 验证分析类型
        valid_types = ["progress", "performance", "behavior"]
        if request.analysis_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"无效的分析类型。支持的类型: {', '.join(valid_types)}"
            )
        
        # 执行学习分析
        result = await analytics_service.analyze_learning_data(request)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"学习分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.post("/qa/intelligent", response_model=QAResponse)
async def intelligent_qa(
    request: QARequest,
    agent_manager = Depends(get_agent_manager_from_state)
):
    """
    智能问答接口
    
    提供智能化的问题解答服务。
    根据问题类型和学习上下文选择合适的智能体进行回答。
    """
    try:
        logger.info(f"智能问答: {request.question[:50]}...")
        
        # 验证问题
        if len(request.question.strip()) < 5:
            raise HTTPException(status_code=400, detail="问题描述过于简短")
        
        # 选择合适的智能体
        agent_type = _select_qa_agent(request.question, request.subject)
        
        # 构建问答上下文
        qa_context = {
            "question": request.question,
            "subject": request.subject,
            "learning_context": request.context.dict() if request.context else None
        }
        
        # 获取智能体回答
        answer = await agent_manager.chat_with_agent(
            agent_type=agent_type,
            message=f"请回答以下问题：{request.question}",
            context=qa_context
        )
        
        # 生成相关主题和后续问题
        related_topics = _extract_related_topics(request.question, answer)
        follow_up_questions = _generate_follow_up_questions(request.question, answer)
        
        # 计算置信度（简化实现）
        confidence = _calculate_answer_confidence(answer)
        
        return QAResponse(
            success=True,
            message="问答成功",
            answer=answer,
            confidence=confidence,
            related_topics=related_topics,
            follow_up_questions=follow_up_questions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"智能问答失败: {e}")
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")

@router.get("/system/health", response_model=HealthCheckResponse)
async def health_check(
    agent_manager = Depends(get_agent_manager_from_state)
):
    """
    系统健康检查接口
    
    检查系统各组件的运行状态，包括智能体服务、配置状态等。
    """
    try:
        # 检查智能体管理器状态
        agent_status = "正常" if agent_manager.initialized else "未初始化"
        
        # 检查各个智能体状态
        expert_agent = agent_manager.get_agent("expert")
        assistant_agent = agent_manager.get_agent("assistant")
        peer_agent = agent_manager.get_agent("peer")
        
        components = {
            "agent_manager": agent_status,
            "expert_agent": "正常" if expert_agent else "不可用",
            "assistant_agent": "正常" if assistant_agent else "不可用",
            "peer_agent": "正常" if peer_agent else "不可用",
            "personalization_service": "正常",
            "deep_learning_service": "正常",
            "analytics_service": "正常"
        }
        
        # 判断整体系统状态
        system_status = "健康" if all(status == "正常" for status in components.values()) else "部分异常"
        
        return HealthCheckResponse(
            success=True,
            message="健康检查完成",
            version=settings.app_version,
            status=system_status,
            components=components
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return HealthCheckResponse(
            success=False,
            message=f"健康检查失败: {str(e)}",
            version=settings.app_version,
            status="异常",
            components={}
        )

# 辅助函数

def _generate_suggestions(agent_type: str, message: str, response: str) -> list:
    """根据智能体类型生成学习建议"""
    suggestions_map = {
        "expert": [
            "深入研究相关理论背景",
            "查阅权威学术资料",
            "尝试从多个角度分析问题"
        ],
        "assistant": [
            "多做相关练习巩固理解",
            "制定学习计划循序渐进",
            "及时复习避免遗忘"
        ],
        "peer": [
            "与同学讨论交流心得",
            "分享学习经验和方法",
            "互相鼓励保持学习动力"
        ]
    }
    
    return suggestions_map.get(agent_type, ["继续保持学习热情"])

def _select_qa_agent(question: str, subject: str) -> str:
    """根据问题类型选择合适的智能体"""
    # 简化的智能体选择逻辑
    if any(keyword in question.lower() for keyword in ["为什么", "原理", "理论", "概念"]):
        return "expert"  # 专家智能体适合回答理论问题
    elif any(keyword in question.lower() for keyword in ["怎么做", "如何", "方法", "步骤"]):
        return "assistant"  # 助教智能体适合回答操作问题
    else:
        return "peer"  # 同伴智能体适合一般性问题

def _extract_related_topics(question: str, answer: str) -> list:
    """提取相关主题"""
    # 简化实现，实际应用中可以使用NLP技术
    topics = []
    
    # 基于关键词提取
    common_topics = ["基础概念", "实践应用", "进阶学习", "相关理论"]
    
    # 随机选择2-3个相关主题
    import random
    topics = random.sample(common_topics, min(3, len(common_topics)))
    
    return topics

def _generate_follow_up_questions(question: str, answer: str) -> list:
    """生成后续问题建议"""
    # 简化实现
    follow_ups = [
        "这个概念在实际中如何应用？",
        "有哪些相关的扩展知识？",
        "如何进一步深入学习？"
    ]
    
    return follow_ups[:2]  # 返回前2个问题

def _calculate_answer_confidence(answer: str) -> float:
    """计算回答置信度"""
    # 简化的置信度计算
    # 实际应用中可以基于模型输出概率、答案长度、关键词匹配等
    
    base_confidence = 0.8
    
    # 根据答案长度调整
    if len(answer) > 200:
        base_confidence += 0.1
    elif len(answer) < 50:
        base_confidence -= 0.2
    
    # 确保在0-1范围内
    return max(0.0, min(1.0, base_confidence))

# 重复定义已删除 - 使用前面的collaborate_chat函数实现