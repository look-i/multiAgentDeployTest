# 智能体路由策略模块
# Agent Router Strategy Module

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from app.models.schemas import LearningContext
from app.core.logging import get_logger

logger = get_logger(__name__)


class AgentType(Enum):
    """智能体类型枚举"""

    EXPERT = "expert"  # 专家智能体 - 适合理论问题、深度分析
    ASSISTANT = "assistant"  # 助教智能体 - 适合操作指导、练习辅导
    PEER = "peer"  # 同伴智能体 - 适合讨论交流、情感支持


@dataclass
class RoutingResult:
    """路由结果数据类"""

    agent_type: AgentType
    confidence: float  # 置信度 0-1
    reason: str  # 选择原因
    fallback_agents: List[AgentType]  # 备选智能体列表


class AgentRouter:
    """智能体路由器

    根据用户问题的类型、内容、学科领域和学习上下文，
    智能选择最适合的智能体来处理用户请求。
    """

    def __init__(self):
        """初始化路由器"""
        self.logger = logger

        # 专家智能体关键词 - 理论性、深度分析类问题
        self.expert_keywords = {
            "理论": [
                "原理",
                "理论",
                "概念",
                "定义",
                "本质",
                "机制",
                "规律",
                "公式",
                "定理",
            ],
            "分析": ["为什么", "原因", "分析", "解释", "探讨", "研究", "深入", "详细"],
            "学术": ["学术", "论文", "研究", "文献", "权威", "专业", "科学", "系统"],
        }

        # 助教智能体关键词 - 操作性、指导类问题
        self.assistant_keywords = {
            "操作": ["怎么做", "如何", "方法", "步骤", "流程", "过程", "操作", "实现"],
            "练习": ["练习", "题目", "作业", "习题", "训练", "巩固", "复习", "检测"],
            "指导": ["指导", "帮助", "教", "学习", "掌握", "提高", "改进", "建议"],
        }

        # 同伴智能体关键词 - 交流性、情感支持类问题
        self.peer_keywords = {
            "交流": ["讨论", "交流", "分享", "聊聊", "谈谈", "看法", "观点", "想法"],
            "情感": ["困难", "挫折", "焦虑", "压力", "鼓励", "支持", "陪伴", "理解"],
            "日常": ["日常", "生活", "经验", "感受", "心情", "状态", "情况", "体验"],
        }

        # 学科领域映射 - 不同学科倾向于不同智能体
        self.subject_preferences = {
            "数学": AgentType.EXPERT,  # 数学更偏向专家解答
            "物理": AgentType.EXPERT,  # 物理更偏向专家解答
            "化学": AgentType.EXPERT,  # 化学更偏向专家解答
            "编程": AgentType.ASSISTANT,  # 编程更偏向助教指导
            "语言": AgentType.PEER,  # 语言学习更偏向同伴交流
            "历史": AgentType.PEER,  # 历史更偏向讨论交流
            "文学": AgentType.PEER,  # 文学更偏向讨论交流
        }

    def route_agent(
        self,
        question: str,
        subject: Optional[str] = None,
        context: Optional[LearningContext] = None,
    ) -> RoutingResult:
        """智能体路由主方法

        Args:
            question: 用户问题
            subject: 学科领域
            context: 学习上下文

        Returns:
            RoutingResult: 路由结果
        """
        try:
            self.logger.info(f"开始路由分析: {question[:50]}...")

            # 1. 基于关键词的初步分析
            keyword_scores = self._analyze_keywords(question)

            # 2. 基于学科领域的分析
            subject_preference = self._analyze_subject(subject)

            # 3. 基于学习上下文的分析
            context_preference = self._analyze_context(context)

            # 4. 综合评分和决策
            final_result = self._make_final_decision(keyword_scores, subject_preference, context_preference, question)

            self.logger.info(f"路由结果: {final_result.agent_type.value}, 置信度: {final_result.confidence:.2f}")
            return final_result

        except Exception as e:
            self.logger.error(f"路由分析失败: {e}")
            # 默认返回助教智能体
            return RoutingResult(
                agent_type=AgentType.ASSISTANT,
                confidence=0.5,
                reason="路由分析异常，使用默认助教智能体",
                fallback_agents=[AgentType.EXPERT, AgentType.PEER],
            )

    def _analyze_keywords(self, question: str) -> Dict[AgentType, float]:
        """基于关键词分析问题类型

        Args:
            question: 用户问题

        Returns:
            Dict[AgentType, float]: 各智能体的关键词匹配分数
        """
        question_lower = question.lower()
        scores = {agent_type: 0.0 for agent_type in AgentType}

        # 分析专家智能体关键词
        for category, keywords in self.expert_keywords.items():
            for keyword in keywords:
                if keyword in question_lower:
                    scores[AgentType.EXPERT] += 1.0

        # 分析助教智能体关键词
        for category, keywords in self.assistant_keywords.items():
            for keyword in keywords:
                if keyword in question_lower:
                    scores[AgentType.ASSISTANT] += 1.0

        # 分析同伴智能体关键词
        for category, keywords in self.peer_keywords.items():
            for keyword in keywords:
                if keyword in question_lower:
                    scores[AgentType.PEER] += 1.0

        # 归一化分数
        max_score = max(scores.values()) if max(scores.values()) > 0 else 1.0
        normalized_scores = {k: v / max_score for k, v in scores.items()}

        return normalized_scores

    def _analyze_subject(self, subject: Optional[str]) -> Tuple[Optional[AgentType], float]:
        """基于学科领域分析智能体偏好

        Args:
            subject: 学科领域

        Returns:
            Tuple[Optional[AgentType], float]: 推荐的智能体类型和置信度
        """
        if not subject:
            return None, 0.0

        subject_lower = subject.lower()
        for subj, preferred_agent in self.subject_preferences.items():
            if subj in subject_lower:
                return preferred_agent, 0.8

        return None, 0.0

    def _analyze_context(self, context: Optional[LearningContext]) -> Tuple[Optional[AgentType], float]:
        """基于学习上下文分析智能体偏好

        Args:
            context: 学习上下文

        Returns:
            Tuple[Optional[AgentType], float]: 推荐的智能体类型和置信度
        """
        if not context:
            return None, 0.0

        # 根据认知状态选择智能体
        cognitive_state = context.cognitive_state

        # 认知负荷高时，选择同伴智能体提供情感支持
        if cognitive_state.cognitive_load > 0.7:
            return AgentType.PEER, 0.6

        # 理解率低时，选择助教智能体提供指导
        if cognitive_state.comprehension_rate < 0.4:
            return AgentType.ASSISTANT, 0.7

        # 学习进度快且理解率高时，选择专家智能体提供深度内容
        if cognitive_state.learning_progress > 0.7 and cognitive_state.comprehension_rate > 0.7:
            return AgentType.EXPERT, 0.6

        return None, 0.0

    def _make_final_decision(
        self,
        keyword_scores: Dict[AgentType, float],
        subject_preference: Tuple[Optional[AgentType], float],
        context_preference: Tuple[Optional[AgentType], float],
        question: str,
    ) -> RoutingResult:
        """综合各种分析结果做出最终决策

        Args:
            keyword_scores: 关键词分析分数
            subject_preference: 学科偏好
            context_preference: 上下文偏好
            question: 原始问题

        Returns:
            RoutingResult: 最终路由结果
        """
        # 初始化综合分数
        final_scores = {agent_type: 0.0 for agent_type in AgentType}

        # 1. 关键词分数权重 40%
        for agent_type, score in keyword_scores.items():
            final_scores[agent_type] += score * 0.4

        # 2. 学科偏好权重 35%
        if subject_preference[0]:
            final_scores[subject_preference[0]] += subject_preference[1] * 0.35

        # 3. 上下文偏好权重 25%
        if context_preference[0]:
            final_scores[context_preference[0]] += context_preference[1] * 0.25

        # 找出得分最高的智能体
        best_agent = max(final_scores, key=final_scores.get)
        best_score = final_scores[best_agent]

        # 如果所有分数都很低，使用默认规则
        if best_score < 0.3:
            return self._apply_default_rules(question)

        # 生成备选智能体列表
        sorted_agents = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        fallback_agents = [agent for agent, score in sorted_agents[1:] if score > 0.1]

        # 生成选择原因
        reason = self._generate_reason(best_agent, keyword_scores, subject_preference, context_preference)

        return RoutingResult(
            agent_type=best_agent,
            confidence=min(best_score, 1.0),
            reason=reason,
            fallback_agents=fallback_agents,
        )

    def _apply_default_rules(self, question: str) -> RoutingResult:
        """应用默认路由规则

        Args:
            question: 用户问题

        Returns:
            RoutingResult: 默认路由结果
        """
        # 简单的默认规则
        if len(question) > 100:  # 长问题倾向于专家
            return RoutingResult(
                agent_type=AgentType.EXPERT,
                confidence=0.6,
                reason="问题较为复杂，选择专家智能体",
                fallback_agents=[AgentType.ASSISTANT, AgentType.PEER],
            )
        elif "?" in question or "？" in question:  # 疑问句倾向于助教
            return RoutingResult(
                agent_type=AgentType.ASSISTANT,
                confidence=0.6,
                reason="问题需要指导解答，选择助教智能体",
                fallback_agents=[AgentType.EXPERT, AgentType.PEER],
            )
        else:  # 默认选择同伴
            return RoutingResult(
                agent_type=AgentType.PEER,
                confidence=0.5,
                reason="一般性交流，选择同伴智能体",
                fallback_agents=[AgentType.ASSISTANT, AgentType.EXPERT],
            )

    def _generate_reason(
        self,
        agent_type: AgentType,
        keyword_scores: Dict[AgentType, float],
        subject_preference: Tuple[Optional[AgentType], float],
        context_preference: Tuple[Optional[AgentType], float],
    ) -> str:
        """生成选择原因说明

        Args:
            agent_type: 选择的智能体类型
            keyword_scores: 关键词分数
            subject_preference: 学科偏好
            context_preference: 上下文偏好

        Returns:
            str: 选择原因
        """
        reasons = []

        # 关键词匹配原因
        if keyword_scores[agent_type] > 0.5:
            if agent_type == AgentType.EXPERT:
                reasons.append("问题涉及理论分析")
            elif agent_type == AgentType.ASSISTANT:
                reasons.append("问题需要操作指导")
            else:
                reasons.append("问题适合交流讨论")

        # 学科偏好原因
        if subject_preference[0] == agent_type and subject_preference[1] > 0.5:
            reasons.append("基于学科特点")

        # 上下文偏好原因
        if context_preference[0] == agent_type and context_preference[1] > 0.5:
            reasons.append("基于学习状态")

        if not reasons:
            reasons.append("综合分析结果")

        return "、".join(reasons)

    def get_agent_capabilities(self, agent_type: AgentType) -> Dict[str, str]:
        """获取智能体能力描述

        Args:
            agent_type: 智能体类型

        Returns:
            Dict[str, str]: 智能体能力描述
        """
        capabilities = {
            AgentType.EXPERT: {
                "name": "专家智能体",
                "description": "擅长理论分析、深度解释和学术问题解答",
                "strengths": "理论知识丰富、分析能力强、解答深入",
                "suitable_for": "概念解释、原理分析、学术讨论",
            },
            AgentType.ASSISTANT: {
                "name": "助教智能体",
                "description": "擅长操作指导、练习辅导和学习建议",
                "strengths": "指导性强、步骤清晰、实用性高",
                "suitable_for": "操作指导、练习辅导、学习规划",
            },
            AgentType.PEER: {
                "name": "同伴智能体",
                "description": "擅长交流讨论、情感支持和经验分享",
                "strengths": "亲和力强、理解性好、支持性高",
                "suitable_for": "讨论交流、情感支持、经验分享",
            },
        }

        return capabilities.get(agent_type, {})
