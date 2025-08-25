import asyncio
from typing import List, Dict, Any, Tuple, Optional
from agentscope.msghub import msghub
from agentscope.message import Msg
from agentscope.agents import AgentBase
from ..models.schemas import ChatSession, Message, AutoConfig
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

    async def collaborate(self, session_id: str, conversation_history: List[Dict[str, Any]], auto_config: Optional[AutoConfig] = None) -> List[Dict[str, Any]]:
        """
        处理用户消息，支持单轮或多轮智能体协作。
        严格遵循无状态原则，每次都接收完整的对话历史。

        Args:
            session_id (str): 会话ID（无状态透传）。
            conversation_history (List[Dict[str, Any]]): 完整的对话历史。
            auto_config (Optional[AutoConfig]): 自动多轮发言配置。

        Returns:
            List[Dict[str, Any]]: 返回智能体响应消息列表（单轮返回1条，多轮返回多条）。
            
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
        
        # 智能体映射表，用于路由决策
        agent_mapping = {
            "expert": expert_agent,
            "assistant": assistant_agent,
            "peer": peer_agent
        }
        
        # 确保路由和参与者智能体都存在
        if not router_agent:
            raise ValueError("路由智能体 'router' 未找到。")
        if not all(participants):
            raise ValueError("一个或多个参与者智能体未找到。")

        # 单轮模式（默认行为，保持向后兼容）
        if not auto_config or not auto_config.enabled:
            return await self._single_round_collaborate(conversation_history, participants, router_agent, agent_mapping)
        
        # 多轮模式：执行连续的智能体发言
        return await self._multi_round_collaborate(conversation_history, participants, router_agent, agent_mapping, auto_config)

    def _is_in_fixed_order_stage(self, history: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """
        判断是否处于固定顺序发言阶段（专家→助教→同伴）。
        兼容中文角色名（专家智能体/助教智能体/同伴智能体）与英文Agent名（ExpertAgent/AssistantAgent/CompanionAgent）。
        返回的智能体key统一使用 expert/assistant/peer，便于与agent_mapping对齐。
        """
        # 统一以三个逻辑键标记是否已发言
        spoken_flags = {
            "expert": False,
            "assistant": False,
            "peer": False,
        }
        
        # 定义别名集合，兼容中文与常见英文Agent命名（去除空格和下划线后做匹配）
        aliases = {
            "expert": {"专家智能体", "expert", "expertagent", "expert_agent"},
            "assistant": {"助教智能体", "assistant", "assistantagent", "assistant_agent"},
            "peer": {"同伴智能体", "peer", "companion", "companionagent", "companion_agent"},
        }
        
        def normalize(name: str) -> str:
            """将名称规整为小写并去除空格与下划线，便于统一匹配"""
            if not isinstance(name, str):
                return ""
            s = name.strip().lower()
            s = s.replace(" ", "").replace("_", "")
            return s
        
        # 遍历历史，标记已发言的智能体（兼容多种别名）
        for msg in history:
            role_raw = msg.get("role", "")
            role_norm = normalize(role_raw)
            for key, alias_set in aliases.items():
                # 将别名也做同样的normalize后再比对
                if role_norm in {normalize(a) for a in alias_set}:
                    spoken_flags[key] = True
        
        # 按固定顺序：专家→助教→同伴，决定下一个应发言的智能体
        if not spoken_flags["expert"]:
            return True, "expert"
        elif not spoken_flags["assistant"]:
            return True, "assistant"
        elif not spoken_flags["peer"]:
            return True, "peer"
        else:
            return False, None  # 已完成固定顺序，进入动态路由阶段

    # 新增：判断是否用户消息与用户介入的辅助函数
    def _is_user_message(self, msg: Dict[str, Any]) -> bool:
        """
        判断一条消息是否为用户消息。
        约定：role 字段为 'user'（不区分大小写）即视为用户消息。
        """
        try:
            role = str(msg.get("role", "")).strip().lower()
        except Exception:
            role = ""
        return role == "user"

    def _detect_user_intervention(self, history: List[Dict[str, Any]]) -> bool:
        """
        检测本次请求是否发生了“用户介入”（即是否包含新的用户发言）。
        无状态判断：仅基于本次请求提供的 history。
        规则：如果 history 存在且最后一条为用户消息，则认为发生了用户介入。
        """
        if not history:
            return False
        last_msg = history[-1]
        return self._is_user_message(last_msg)

    async def _single_round_collaborate(self, history: List[Dict[str, Any]], participants: List[AgentBase], 
                                     router_agent: AgentBase, agent_mapping: Dict[str, AgentBase]) -> List[Dict[str, Any]]:
        """
        单轮协作逻辑（保持现有逻辑不变，确保向后兼容）。
        
        Args:
            history: 对话历史
            participants: 参与者智能体列表
            router_agent: 路由智能体
            agent_mapping: 智能体映射表
            
        Returns:
            单个智能体的响应列表
        """
        # 将字典列表转换为AgentScope的Msg对象列表，用于智能体处理
        scoped_history = [
            Msg(
                name=msg.get("role", "unknown"),
                content=msg.get("content", ""),
                role=("user" if str(msg.get("role", "")).lower() == "user" else "assistant"),
            )
            for msg in history
        ]

        # 使用msghub进行消息上下文管理
        with msghub(participants=participants) as hub:
            # 调用路由智能体决定下一个发言者
            next_speaker_msg = await asyncio.to_thread(router_agent, scoped_history)
            next_choice = next_speaker_msg.content

            # 解析路由决策结果
            agent_key, selected_agent = self._parse_routing_decision(next_choice, agent_mapping)

            # 获取选定智能体的响应
            response_msg = await asyncio.to_thread(selected_agent, scoped_history)
            
            # 格式化响应以符合API规范（使用role字段匹配Message模型）
            response = {"role": response_msg.name, "content": response_msg.content}

            return [response]

    async def _multi_round_collaborate(self, history: List[Dict[str, Any]], participants: List[AgentBase],
                                     router_agent: AgentBase, agent_mapping: Dict[str, AgentBase], 
                                     auto_config: AutoConfig) -> List[Dict[str, Any]]:
        """
        多轮协作逻辑：支持固定顺序阶段和动态路由阶段。
        
        Args:
            history: 对话历史
            participants: 参与者智能体列表  
            router_agent: 路由智能体
            agent_mapping: 智能体映射表
            auto_config: 自动多轮配置
            
        Returns:
            多个智能体的响应列表
        """
        responses = []
        current_history = history.copy()
        max_rounds = auto_config.max_rounds
        
        # 阶段化计数变量
        rounds_done = 0  # 已执行的总轮次
        entered_dynamic = False  # 是否已进入动态路由阶段
        dynamic_rounds_done = 0  # 动态路由阶段已执行轮次
        dynamic_max_rounds = max_rounds  # 动态路由阶段轮次限制
        
        # 用户介入检测（仅用于动态路由阶段）
        user_just_spoke = self._detect_user_intervention(current_history)

        for round_num in range(max_rounds):
            # 检查是否在固定顺序阶段
            in_fixed_stage, next_fixed_agent = self._is_in_fixed_order_stage(current_history)
            
            if in_fixed_stage and next_fixed_agent:
                # 固定顺序发言：按专家→助教→同伴的顺序，完全忽略 continue_on_user_input
                selected_agent = agent_mapping[next_fixed_agent]
                agent_key = next_fixed_agent
            else:
                # 首次进入动态路由阶段：根据用户介入和配置设置轮次限制
                if not entered_dynamic:
                    entered_dynamic = True
                    # 仅在动态路由阶段应用 continue_on_user_input 控制
                    if user_just_spoke and not getattr(auto_config, "continue_on_user_input", False):
                        dynamic_max_rounds = 1  # 限制动态路由阶段只执行1轮
                    else:
                        dynamic_max_rounds = max_rounds - rounds_done  # 剩余轮次
                
                # 检查动态路由阶段轮次限制
                if dynamic_rounds_done >= dynamic_max_rounds:
                    break
                
                # 动态路由决策：由路由智能体决定下一个发言者
                agent_key, selected_agent = await self._route_next_speaker(current_history, router_agent, agent_mapping)
                
                # 检查停止信号
                if agent_key == "STOP":
                    break
                
                dynamic_rounds_done += 1
            
            # 获取智能体响应
            try:
                response = await self._get_agent_response(selected_agent, current_history, participants)
                responses.append(response)
                
                # 更新历史记录，为下一轮做准备
                current_history.append(response)
                
                # 检查停止关键词（做大小写与空白规范化，提高鲁棒性）
                content_norm = str(response.get("content", "")).strip().lower()
                keywords = auto_config.stop_keywords or []
                keywords_norm = [str(k).strip().lower() for k in keywords]
                if any(k and k in content_norm for k in keywords_norm):
                    break
                    
            except Exception as e:
                # 如果智能体响应失败，记录错误并跳出循环
                import logging
                logging.error(f"智能体 {agent_key} 响应失败: {str(e)}")
                break
            
            rounds_done += 1

        return responses

    def _parse_routing_decision(self, decision_content: str, agent_mapping: Dict[str, AgentBase]) -> Tuple[str, AgentBase]:
        """
        解析路由智能体的决策结果，支持JSON格式和简单字符串格式。
        
        Args:
            decision_content: 路由智能体返回的决策内容
            agent_mapping: 智能体映射表
            
        Returns:
            Tuple[str, AgentBase]: (智能体key, 智能体实例)
        """
        # 目标：优先解析JSON字符串 {"agent": "expert", "reason": "..."}；
        # 兼容纯字符串("expert"/"assistant"/"peer").
        next_agent_key: Optional[str] = None
        try:
            # 如果是字符串且看起来像JSON，优先尝试解析
            if isinstance(decision_content, str):
                stripped = decision_content.strip()
                if stripped.startswith("{") and stripped.endswith("}"):
                    import json
                    parsed = json.loads(stripped)
                    next_agent_key = parsed.get("agent")
                else:
                    # 纯字符串直接作为候选键
                    next_agent_key = stripped
            else:
                # 非字符串，转成字符串后尝试解析
                import json
                parsed = json.loads(str(decision_content))
                next_agent_key = parsed.get("agent")
        except Exception:
            # 解析失败则回退到直接使用字符串内容
            next_agent_key = str(decision_content).strip()

        # 统一小写，去除引号和多余空格
        if isinstance(next_agent_key, str):
            next_agent_key = next_agent_key.strip().strip('"\'').lower()
        else:
            next_agent_key = "expert"

        # 有效键映射
        valid_keys = {
            "expert": agent_mapping["expert"],
            "assistant": agent_mapping["assistant"],
            "peer": agent_mapping["peer"],
        }
        # 选择对应智能体，默认回退expert
        selected_agent = valid_keys.get(next_agent_key, agent_mapping["expert"])
        return next_agent_key or "expert", selected_agent

    async def _route_next_speaker(self, history: List[Dict[str, Any]], router_agent: AgentBase, 
                                agent_mapping: Dict[str, AgentBase]) -> Tuple[str, AgentBase]:
        """
        通过路由智能体决定下一个发言者。
        
        Args:
            history: 对话历史
            router_agent: 路由智能体
            agent_mapping: 智能体映射表
            
        Returns:
            Tuple[str, AgentBase]: (智能体key或"STOP", 智能体实例或None)
        """
        # 将历史转换为Msg格式
        scoped_history = [
            Msg(
                name=msg.get("role", "unknown"),
                content=msg.get("content", ""),
                role=("user" if str(msg.get("role", "")).lower() == "user" else "assistant"),
            )
            for msg in history
        ]
        
        # 调用路由智能体进行决策
        try:
            next_speaker_msg = await asyncio.to_thread(router_agent, scoped_history)
            decision_content = next_speaker_msg.content
            
            # 检查是否为停止信号
            if "STOP" in str(decision_content).upper():
                return "STOP", None
                
            # 解析普通的路由决策
            agent_key, selected_agent = self._parse_routing_decision(decision_content, agent_mapping)
            return agent_key, selected_agent
            
        except Exception as e:
            # 路由失败时默认选择专家智能体
            import logging
            logging.error(f"路由决策失败: {str(e)}")
            return "expert", agent_mapping["expert"]

    async def _get_agent_response(self, agent: AgentBase, history: List[Dict[str, Any]], 
                                participants: List[AgentBase]) -> Dict[str, Any]:
        """
        获取指定智能体的响应。
        
        Args:
            agent: 目标智能体
            history: 对话历史
            participants: 参与者列表
            
        Returns:
            格式化的智能体响应字典
        """
        # 转换历史格式
        scoped_history = [
            Msg(
                name=msg.get("role", "unknown"),
                content=msg.get("content", ""),
                role=("user" if str(msg.get("role", "")).lower() == "user" else "assistant"),
            )
            for msg in history
        ]
        
        # 使用msghub获取智能体响应
        with msghub(participants=participants) as hub:
            response_msg = await asyncio.to_thread(agent, scoped_history)
            
            # 格式化响应以符合API规范
            return {"role": response_msg.name, "content": response_msg.content}
