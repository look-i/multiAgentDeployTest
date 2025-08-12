import asyncio
from typing import List, Dict, Any, Tuple
from agentscope.msghub import msghub
from agentscope.message import Msg
from agentscope.agents import AgentBase
from ..models.schemas import ChatSession, Message
from .agent_manager import AgentManager

class ChatManager:
    """
    管理多智能体聊天会话，包括会话生命周期、工作流编排和消息广播。
    """
    def __init__(self, agent_manager: AgentManager):
        """
        初始化ChatManager。
        注意：构造函数中不再获取智能体实例，以避免在AgentManager完全初始化前调用。

        Args:
            agent_manager (AgentManager): 智能体管理器实例。
        """
        self.agent_manager = agent_manager
        # 注意：在无状态架构中，我们不在内存中存储会话
        # self.sessions: Dict[str, ChatSession] = {}

    async def init_session(self) -> Tuple[str, ChatSession, List[Dict[str, Any]]]:
        """
        初始化一个新的聊天会话，并返回会话ID、会话对象和初始的智能体发言。
        此方法在每次会话开始时调用，以确保获取到最新的、已完全初始化的智能体实例。

        Returns:
            Tuple[str, ChatSession, List[Dict[str, Any]]]: 返回会话ID、会话对象和开场白消息列表。
        
        Raises:
            ValueError: 如果缺少深度学习模式所需的任何智能体。
        """
        import uuid
        
        # 在方法内部获取智能体，确保它们已经被AgentManager完全初始化
        expert_agent = self.agent_manager.get_agent("expert")
        assistant_agent = self.agent_manager.get_agent("assistant")
        companion_agent = self.agent_manager.get_agent("peer")

        # 检查所有必要的智能体是否都已成功获取
        if not all([expert_agent, assistant_agent, companion_agent]):
            # 抛出错误，明确指出哪些智能体缺失，有助于快速定位问题
            missing_agents = [
                name for name, agent in [
                    ("expert", expert_agent),
                    ("assistant", assistant_agent),
                    ("peer", companion_agent)
                ] if not agent
            ]
            raise ValueError(f"缺少深度学习模式所需的智能体: {', '.join(missing_agents)}")

        # 生成会话ID
        session_id = str(uuid.uuid4())

        # 定义初始发言顺序和内容
        initial_agents = [expert_agent, assistant_agent, companion_agent]
        initial_messages = [
            Msg(name="ExpertAgent", content="你好，我是你的专家智能体，负责为你提供专业的知识和概念解释。", role="assistant"),
            Msg(name="AssistantAgent", content="你好，我是你的助教智能体，将为你分解任务、提供操作指导。", role="assistant"),
            Msg(name="CompanionAgent", content="你好，我是你的同伴智能体，会通过实例演示来帮助你更好地理解。我们开始学习吧！", role="assistant"),
        ]

        # 创建会话对象，但不存储它，以符合无状态原则
        session = ChatSession(
            participants=[agent.name for agent in initial_agents],
            history=[Message(role=msg.name, content=msg.content) for msg in initial_messages]
        )

        # 格式化开场白用于API响应
        opening_remarks = [{"agent_name": msg.name, "content": msg.content} for msg in initial_messages]
        
        return session_id, session, opening_remarks

    async def collaborate(self, session_id: str, conversation_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理用户消息，通过路由智能体决定下一个发言的智能体，并返回其响应。
        严格遵循无状态原则，每次都接收完整的对话历史。

        Args:
            session_id (str): 会话ID（无状态透传）。
            conversation_history (List[Dict[str, Any]]): 完整的对话历史。

        Returns:
            List[Dict[str, Any]]: 返回智能体响应消息列表。
            
        Raises:
            ValueError: 如果路由智能体或参与者智能体未找到。
        """
        # 动态获取所有参与的智能体（使用小写键，与AgentManager存储一致）
        expert_agent = self.agent_manager.get_agent("expert")
        assistant_agent = self.agent_manager.get_agent("assistant")
        peer_agent = self.agent_manager.get_agent("peer")
        router_agent = self.agent_manager.get_agent("router")

        participants: List[AgentBase] = [
            expert_agent,
            assistant_agent,
            peer_agent
        ]
        
        # 确保路由和参与者智能体都存在
        if not router_agent:
            raise ValueError("路由智能体 'router' 未找到。")
        if not all(participants):
            raise ValueError("一个或多个参与者智能体未找到。")

        # 将字典列表转换为AgentScope的Msg对象列表，用于智能体处理
        # 注意：AgentScope 0.1.6 的 Msg 需要显式提供 role 参数
        # 这里的约定：如果历史记录中的 role 为 "user"（不区分大小写），则 Msg.role 赋值为 "user"；
        # 否则一律视为智能体消息，Msg.role 赋值为 "assistant"。
        scoped_history = [
            Msg(
                name=msg.get("role", "unknown"),
                content=msg.get("content", ""),
                role=("user" if str(msg.get("role", "")).lower() == "user" else "assistant"),
            )
            for msg in conversation_history
        ]

        # 使用msghub进行消息上下文管理
        with msghub(participants=participants) as hub:
            # 调用路由智能体决定下一个发言者
            # ReActAgentV2 返回的是 Msg 对象，其 content 期望是 JSON 字符串或简单标识
            next_speaker_msg = await asyncio.to_thread(
                router_agent,
                scoped_history
            )
            next_choice = next_speaker_msg.content

            # 兼容JSON格式: {"agent": "expert", "reason": "..."}
            next_agent_key = None
            if isinstance(next_choice, str):
                next_agent_key = next_choice.strip()
            else:
                try:
                    import json
                    parsed = json.loads(str(next_choice))
                    next_agent_key = parsed.get("agent")
                except Exception:
                    next_agent_key = None

            # 映射到参与者键
            valid_keys = {"expert": expert_agent, "assistant": assistant_agent, "peer": peer_agent}
            next_speaker_agent = valid_keys.get(next_agent_key, expert_agent)  # 默认专家

            # 获取选定智能体的响应
            response_msg = await asyncio.to_thread(
                next_speaker_agent,
                scoped_history
            )
            
            # 格式化响应以符合API规范（使用role字段匹配Message模型）
            response = {"role": response_msg.name, "content": response_msg.content}

            return [response]
