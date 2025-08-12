# 对话状态管理模块
# Conversation State Management Module

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
from collections import defaultdict

from app.models.schemas import LearningContext, CognitiveState, LearningStyleData
from app.core.logging import get_logger

logger = get_logger(__name__)


class StateType(Enum):
    """状态类型枚举"""

    CONVERSATION = "conversation"  # 对话状态
    LEARNING = "learning"  # 学习状态
    COGNITIVE = "cognitive"  # 认知状态
    CONTEXT = "context"  # 上下文状态
    SESSION = "session"  # 会话状态


class StateTransition(Enum):
    """状态转换类型枚举"""

    INIT = "init"  # 初始化
    UPDATE = "update"  # 更新
    PAUSE = "pause"  # 暂停
    RESUME = "resume"  # 恢复
    COMPLETE = "complete"  # 完成
    ERROR = "error"  # 错误
    RESET = "reset"  # 重置


@dataclass
class StateSnapshot:
    """状态快照数据类"""

    id: str
    session_id: str
    state_type: StateType
    timestamp: datetime
    data: Dict[str, Any]
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationState:
    """对话状态数据类"""

    session_id: str
    current_topic: Optional[str] = None
    topic_history: List[str] = field(default_factory=list)
    message_count: int = 0
    last_agent_type: Optional[str] = None
    conversation_flow: List[Dict[str, Any]] = field(default_factory=list)
    context_switches: int = 0
    engagement_level: float = 0.5  # 0-1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningState:
    """学习状态数据类"""

    session_id: str
    current_subject: Optional[str] = None
    learning_objectives: List[str] = field(default_factory=list)
    completed_objectives: List[str] = field(default_factory=list)
    difficulty_level: int = 1  # 1-5
    progress_percentage: float = 0.0  # 0-100
    learning_path: List[str] = field(default_factory=list)
    mastery_levels: Dict[str, float] = field(default_factory=dict)  # topic -> mastery (0-1)
    study_time_minutes: int = 0
    break_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class StateManager:
    """对话状态管理器

    负责跟踪和管理对话状态、学习状态、认知状态等，
    提供状态持久化、状态转换和上下文连续性功能。
    """

    def __init__(self):
        """初始化状态管理器"""
        self.logger = logger

        # 状态存储 (生产环境中应使用数据库)
        self.conversation_states: Dict[str, ConversationState] = {}
        self.learning_states: Dict[str, LearningState] = {}
        self.cognitive_states: Dict[str, CognitiveState] = {}
        self.context_states: Dict[str, LearningContext] = {}

        # 状态快照存储
        self.state_snapshots: Dict[str, List[StateSnapshot]] = defaultdict(list)

        # 状态转换历史
        self.transition_history: Dict[str, List[Tuple[StateTransition, datetime, Dict[str, Any]]]] = defaultdict(list)

        # 状态监控指标
        self.state_metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "state_updates": 0,
            "context_switches": 0,
            "average_session_duration": 0.0,
        }

    def initialize_session_state(
        self,
        session_id: str,
        user_id: str,
        initial_context: Optional[LearningContext] = None,
    ) -> bool:
        """初始化会话状态

        Args:
            session_id: 会话ID
            user_id: 用户ID
            initial_context: 初始学习上下文

        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info(f"初始化会话状态: {session_id}")

            # 初始化对话状态
            conversation_state = ConversationState(session_id=session_id)
            self.conversation_states[session_id] = conversation_state

            # 初始化学习状态
            learning_state = LearningState(session_id=session_id)
            self.learning_states[session_id] = learning_state

            # 初始化认知状态
            if initial_context and initial_context.cognitive_state:
                cognitive_state = initial_context.cognitive_state
            else:
                cognitive_state = CognitiveState(
                    cognitive_load=0.3,
                    attention_level=0.8,
                    comprehension_rate=0.7,
                    learning_progress=0.0,
                )
            self.cognitive_states[session_id] = cognitive_state

            # 初始化上下文状态
            if initial_context:
                self.context_states[session_id] = initial_context
            else:
                # 创建默认上下文
                default_context = LearningContext(
                    user_id=user_id,
                    session_id=session_id,
                    learning_style=LearningStyleData(visual=0.25, auditory=0.25, reading=0.25, kinesthetic=0.25),
                    cognitive_state=cognitive_state,
                )
                self.context_states[session_id] = default_context

            # 记录状态转换
            self._record_state_transition(
                session_id,
                StateTransition.INIT,
                {
                    "user_id": user_id,
                    "has_initial_context": initial_context is not None,
                },
            )

            # 创建初始状态快照
            self._create_state_snapshot(
                session_id,
                StateType.SESSION,
                {
                    "conversation_state": conversation_state.__dict__,
                    "learning_state": learning_state.__dict__,
                    "cognitive_state": cognitive_state.__dict__,
                },
            )

            # 更新指标
            self.state_metrics["total_sessions"] += 1
            self.state_metrics["active_sessions"] += 1

            return True

        except Exception as e:
            self.logger.error(f"初始化会话状态失败: {e}")
            return False

    def update_conversation_state(
        self,
        session_id: str,
        message: str,
        agent_type: str,
        topic: Optional[str] = None,
    ) -> bool:
        """更新对话状态

        Args:
            session_id: 会话ID
            message: 消息内容
            agent_type: 智能体类型
            topic: 当前话题

        Returns:
            bool: 更新是否成功
        """
        try:
            conversation_state = self.conversation_states.get(session_id)
            if not conversation_state:
                self.logger.warning(f"会话状态不存在: {session_id}")
                return False

            # 更新基本信息
            conversation_state.message_count += 1
            conversation_state.updated_at = datetime.now()

            # 检测话题切换
            if topic and topic != conversation_state.current_topic:
                if conversation_state.current_topic:
                    conversation_state.topic_history.append(conversation_state.current_topic)
                    conversation_state.context_switches += 1
                    self.state_metrics["context_switches"] += 1

                conversation_state.current_topic = topic

            # 更新智能体信息
            if agent_type != conversation_state.last_agent_type:
                conversation_state.last_agent_type = agent_type

            # 记录对话流程
            flow_entry = {
                "timestamp": datetime.now().isoformat(),
                "agent_type": agent_type,
                "message_length": len(message),
                "topic": topic,
            }
            conversation_state.conversation_flow.append(flow_entry)

            # 更新参与度（基于消息频率和长度）
            self._update_engagement_level(conversation_state, message)

            # 记录状态转换
            self._record_state_transition(
                session_id,
                StateTransition.UPDATE,
                {
                    "type": "conversation",
                    "agent_type": agent_type,
                    "topic_changed": topic != conversation_state.current_topic,
                    "message_count": conversation_state.message_count,
                },
            )

            self.state_metrics["state_updates"] += 1
            return True

        except Exception as e:
            self.logger.error(f"更新对话状态失败: {e}")
            return False

    def update_learning_state(
        self,
        session_id: str,
        subject: Optional[str] = None,
        objectives: Optional[List[str]] = None,
        progress: Optional[float] = None,
        difficulty: Optional[int] = None,
    ) -> bool:
        """更新学习状态

        Args:
            session_id: 会话ID
            subject: 学科
            objectives: 学习目标
            progress: 学习进度
            difficulty: 难度等级

        Returns:
            bool: 更新是否成功
        """
        try:
            learning_state = self.learning_states.get(session_id)
            if not learning_state:
                self.logger.warning(f"学习状态不存在: {session_id}")
                return False

            # 更新学科
            if subject and subject != learning_state.current_subject:
                learning_state.current_subject = subject

            # 更新学习目标
            if objectives:
                learning_state.learning_objectives.extend(
                    [obj for obj in objectives if obj not in learning_state.learning_objectives]
                )

            # 更新进度
            if progress is not None:
                learning_state.progress_percentage = max(0, min(100, progress))

            # 更新难度
            if difficulty is not None:
                learning_state.difficulty_level = max(1, min(5, difficulty))

            learning_state.updated_at = datetime.now()

            # 计算学习时间
            session_duration = (learning_state.updated_at - learning_state.created_at).total_seconds() / 60
            learning_state.study_time_minutes = int(session_duration)

            # 记录状态转换
            self._record_state_transition(
                session_id,
                StateTransition.UPDATE,
                {
                    "type": "learning",
                    "subject": subject,
                    "progress": progress,
                    "difficulty": difficulty,
                },
            )

            return True

        except Exception as e:
            self.logger.error(f"更新学习状态失败: {e}")
            return False

    def update_cognitive_state(
        self,
        session_id: str,
        cognitive_load: Optional[float] = None,
        attention_level: Optional[float] = None,
        comprehension_rate: Optional[float] = None,
        learning_progress: Optional[float] = None,
    ) -> bool:
        """更新认知状态

        Args:
            session_id: 会话ID
            cognitive_load: 认知负荷
            attention_level: 注意力水平
            comprehension_rate: 理解率
            learning_progress: 学习进度

        Returns:
            bool: 更新是否成功
        """
        try:
            cognitive_state = self.cognitive_states.get(session_id)
            if not cognitive_state:
                self.logger.warning(f"认知状态不存在: {session_id}")
                return False

            # 更新认知指标
            if cognitive_load is not None:
                cognitive_state.cognitive_load = max(0, min(1, cognitive_load))

            if attention_level is not None:
                cognitive_state.attention_level = max(0, min(1, attention_level))

            if comprehension_rate is not None:
                cognitive_state.comprehension_rate = max(0, min(1, comprehension_rate))

            if learning_progress is not None:
                cognitive_state.learning_progress = max(0, min(1, learning_progress))

            # 记录状态转换
            self._record_state_transition(
                session_id,
                StateTransition.UPDATE,
                {
                    "type": "cognitive",
                    "cognitive_load": cognitive_load,
                    "attention_level": attention_level,
                    "comprehension_rate": comprehension_rate,
                    "learning_progress": learning_progress,
                },
            )

            return True

        except Exception as e:
            self.logger.error(f"更新认知状态失败: {e}")
            return False

    def get_session_context(self, session_id: str) -> Optional[LearningContext]:
        """获取会话上下文

        Args:
            session_id: 会话ID

        Returns:
            Optional[LearningContext]: 学习上下文
        """
        context = self.context_states.get(session_id)
        if not context:
            return None

        # 更新上下文中的认知状态
        cognitive_state = self.cognitive_states.get(session_id)
        if cognitive_state:
            context.cognitive_state = cognitive_state

        # 更新当前话题
        conversation_state = self.conversation_states.get(session_id)
        if conversation_state and conversation_state.current_topic:
            context.current_topic = conversation_state.current_topic

        return context

    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取对话历史

        Args:
            session_id: 会话ID
            limit: 返回条数限制

        Returns:
            List[Dict[str, Any]]: 对话历史
        """
        conversation_state = self.conversation_states.get(session_id)
        if not conversation_state:
            return []

        return conversation_state.conversation_flow[-limit:] if conversation_state.conversation_flow else []

    def analyze_learning_pattern(self, session_id: str) -> Dict[str, Any]:
        """分析学习模式

        Args:
            session_id: 会话ID

        Returns:
            Dict[str, Any]: 学习模式分析结果
        """
        conversation_state = self.conversation_states.get(session_id)
        learning_state = self.learning_states.get(session_id)
        cognitive_state = self.cognitive_states.get(session_id)

        if not all([conversation_state, learning_state, cognitive_state]):
            return {"error": "状态数据不完整"}

        # 分析对话模式
        agent_usage = defaultdict(int)
        for flow in conversation_state.conversation_flow:
            agent_usage[flow["agent_type"]] += 1

        # 分析学习偏好
        preferred_agent = max(agent_usage, key=agent_usage.get) if agent_usage else "unknown"

        # 分析学习效率
        efficiency_score = self._calculate_learning_efficiency(conversation_state, learning_state, cognitive_state)

        return {
            "session_id": session_id,
            "total_messages": conversation_state.message_count,
            "topic_switches": conversation_state.context_switches,
            "engagement_level": conversation_state.engagement_level,
            "preferred_agent": preferred_agent,
            "agent_usage": dict(agent_usage),
            "learning_progress": learning_state.progress_percentage,
            "study_time_minutes": learning_state.study_time_minutes,
            "efficiency_score": efficiency_score,
            "cognitive_load": cognitive_state.cognitive_load,
            "comprehension_rate": cognitive_state.comprehension_rate,
            "recommendations": self._generate_learning_recommendations(
                conversation_state, learning_state, cognitive_state
            ),
        }

    def pause_session(self, session_id: str) -> bool:
        """暂停会话

        Args:
            session_id: 会话ID

        Returns:
            bool: 暂停是否成功
        """
        try:
            # 创建暂停时的状态快照
            self._create_comprehensive_snapshot(session_id, "pause")

            # 记录状态转换
            self._record_state_transition(
                session_id,
                StateTransition.PAUSE,
                {"timestamp": datetime.now().isoformat()},
            )

            self.logger.info(f"会话已暂停: {session_id}")
            return True

        except Exception as e:
            self.logger.error(f"暂停会话失败: {e}")
            return False

    def resume_session(self, session_id: str) -> bool:
        """恢复会话

        Args:
            session_id: 会话ID

        Returns:
            bool: 恢复是否成功
        """
        try:
            # 检查会话是否存在
            if session_id not in self.conversation_states:
                self.logger.warning(f"尝试恢复不存在的会话: {session_id}")
                return False

            # 记录状态转换
            self._record_state_transition(
                session_id,
                StateTransition.RESUME,
                {"timestamp": datetime.now().isoformat()},
            )

            self.logger.info(f"会话已恢复: {session_id}")
            return True

        except Exception as e:
            self.logger.error(f"恢复会话失败: {e}")
            return False

    def complete_session(self, session_id: str) -> bool:
        """完成会话

        Args:
            session_id: 会话ID

        Returns:
            bool: 完成是否成功
        """
        try:
            # 创建最终状态快照
            self._create_comprehensive_snapshot(session_id, "complete")

            # 记录状态转换
            self._record_state_transition(
                session_id,
                StateTransition.COMPLETE,
                {
                    "timestamp": datetime.now().isoformat(),
                    "final_analysis": self.analyze_learning_pattern(session_id),
                },
            )

            # 更新指标
            self.state_metrics["active_sessions"] -= 1

            self.logger.info(f"会话已完成: {session_id}")
            return True

        except Exception as e:
            self.logger.error(f"完成会话失败: {e}")
            return False

    def cleanup_session(self, session_id: str) -> bool:
        """清理会话状态

        Args:
            session_id: 会话ID

        Returns:
            bool: 清理是否成功
        """
        try:
            # 移除各种状态
            self.conversation_states.pop(session_id, None)
            self.learning_states.pop(session_id, None)
            self.cognitive_states.pop(session_id, None)
            self.context_states.pop(session_id, None)

            # 保留状态快照和转换历史用于分析
            # 在生产环境中可能需要定期清理

            self.logger.info(f"会话状态已清理: {session_id}")
            return True

        except Exception as e:
            self.logger.error(f"清理会话状态失败: {e}")
            return False

    def _update_engagement_level(self, conversation_state: ConversationState, message: str):
        """更新参与度水平

        Args:
            conversation_state: 对话状态
            message: 消息内容
        """
        # 基于消息长度和频率计算参与度
        message_length_score = min(len(message) / 100, 1.0)  # 消息长度分数

        # 基于时间间隔计算活跃度
        time_since_last = (datetime.now() - conversation_state.updated_at).total_seconds()
        activity_score = max(0, 1 - time_since_last / 300)  # 5分钟内活跃度最高

        # 综合计算参与度
        new_engagement = message_length_score * 0.4 + activity_score * 0.6

        # 平滑更新参与度
        conversation_state.engagement_level = conversation_state.engagement_level * 0.7 + new_engagement * 0.3

    def _calculate_learning_efficiency(
        self,
        conversation_state: ConversationState,
        learning_state: LearningState,
        cognitive_state: CognitiveState,
    ) -> float:
        """计算学习效率

        Args:
            conversation_state: 对话状态
            learning_state: 学习状态
            cognitive_state: 认知状态

        Returns:
            float: 学习效率分数 (0-1)
        """
        # 基于多个因素计算效率
        factors = {
            "progress_rate": learning_state.progress_percentage / max(learning_state.study_time_minutes, 1),
            "comprehension": cognitive_state.comprehension_rate,
            "engagement": conversation_state.engagement_level,
            "focus": 1 - cognitive_state.cognitive_load,
            "consistency": 1 / max(conversation_state.context_switches + 1, 1),
        }

        # 加权平均
        weights = {
            "progress_rate": 0.3,
            "comprehension": 0.25,
            "engagement": 0.2,
            "focus": 0.15,
            "consistency": 0.1,
        }

        efficiency = sum(factors[key] * weights[key] for key in factors)
        return max(0, min(1, efficiency))

    def _generate_learning_recommendations(
        self,
        conversation_state: ConversationState,
        learning_state: LearningState,
        cognitive_state: CognitiveState,
    ) -> List[str]:
        """生成学习建议

        Args:
            conversation_state: 对话状态
            learning_state: 学习状态
            cognitive_state: 认知状态

        Returns:
            List[str]: 学习建议列表
        """
        recommendations = []

        # 基于认知负荷的建议
        if cognitive_state.cognitive_load > 0.7:
            recommendations.append("建议适当休息，降低学习强度")

        # 基于理解率的建议
        if cognitive_state.comprehension_rate < 0.5:
            recommendations.append("建议放慢学习节奏，加强基础理解")

        # 基于参与度的建议
        if conversation_state.engagement_level < 0.4:
            recommendations.append("建议尝试更互动的学习方式")

        # 基于话题切换的建议
        if conversation_state.context_switches > 5:
            recommendations.append("建议专注于单一主题，避免频繁切换")

        # 基于学习进度的建议
        if learning_state.progress_percentage < 20 and learning_state.study_time_minutes > 30:
            recommendations.append("建议调整学习策略，提高学习效率")

        return recommendations if recommendations else ["继续保持良好的学习状态"]

    def _create_state_snapshot(self, session_id: str, state_type: StateType, data: Dict[str, Any]):
        """创建状态快照

        Args:
            session_id: 会话ID
            state_type: 状态类型
            data: 状态数据
        """
        snapshot = StateSnapshot(
            id=str(uuid.uuid4()),
            session_id=session_id,
            state_type=state_type,
            timestamp=datetime.now(),
            data=data,
        )

        self.state_snapshots[session_id].append(snapshot)

    def _create_comprehensive_snapshot(self, session_id: str, reason: str):
        """创建综合状态快照

        Args:
            session_id: 会话ID
            reason: 快照原因
        """
        comprehensive_data = {
            "reason": reason,
            "conversation_state": self.conversation_states.get(session_id, {}).__dict__,
            "learning_state": self.learning_states.get(session_id, {}).__dict__,
            "cognitive_state": self.cognitive_states.get(session_id, {}).__dict__,
            "context_state": (
                self.context_states.get(session_id, {}).__dict__ if self.context_states.get(session_id) else {}
            ),
        }

        self._create_state_snapshot(session_id, StateType.SESSION, comprehensive_data)

    def _record_state_transition(self, session_id: str, transition: StateTransition, metadata: Dict[str, Any]):
        """记录状态转换

        Args:
            session_id: 会话ID
            transition: 转换类型
            metadata: 转换元数据
        """
        self.transition_history[session_id].append((transition, datetime.now(), metadata))

    def get_state_statistics(self) -> Dict[str, Any]:
        """获取状态统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        # 计算平均会话时长
        total_duration = 0
        session_count = 0

        for session_id, conversation_state in self.conversation_states.items():
            duration = (conversation_state.updated_at - conversation_state.created_at).total_seconds() / 60
            total_duration += duration
            session_count += 1

        avg_duration = total_duration / session_count if session_count > 0 else 0
        self.state_metrics["average_session_duration"] = avg_duration

        return {
            "metrics": self.state_metrics.copy(),
            "active_sessions": len(self.conversation_states),
            "total_snapshots": sum(len(snapshots) for snapshots in self.state_snapshots.values()),
            "total_transitions": sum(len(transitions) for transitions in self.transition_history.values()),
        }
