# AgentScope智能体管理器
# AgentScope Agent Manager

import json
from typing import Dict, Any, Optional
from pathlib import Path

import agentscope
from agentscope.agents import DialogAgent, ReActAgentV2
from agentscope.message import Msg
from agentscope.service import ServiceToolkit

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger("app.agent_manager")


class AgentManager:
    """AgentScope智能体管理器"""

    def __init__(self):
        self.agents: Dict[str, DialogAgent] = {}
        self.initialized = False

    async def initialize(self) -> None:
        """初始化AgentScope和智能体"""
        try:
            # 动态构建模型配置，直接使用环境变量值
            model_configs = self._build_model_configs()

            # 初始化AgentScope
            agentscope.init(
                model_configs=model_configs,
                project="EduCube-Nexus",
                name="EduCube-AI-System",  # 使用英文名称避免路径中的中文字符导致监控问题
                logger_level=settings.agentscope_logging_level,
            )

            # 创建智能体实例
            await self._create_agents()

            self.initialized = True
            logger.info("AgentScope智能体管理器初始化完成")

        except Exception as e:
            logger.error(f"AgentScope初始化失败: {e}")
            raise

    def _build_model_configs(self) -> list:
        """动态构建模型配置，直接使用环境变量值"""
        # 基础配置模板
        base_config = {
            "model_type": "openai_chat",
            "model_name": settings.moonshot_model,
            "api_key": settings.moonshot_api_key,  # 直接使用实际的API密钥值
            "client_args": {
                "base_url": settings.moonshot_base_url  # 正确的base_url配置方式
            },
            "organization": None,
        }

        # 构建四个不同的模型配置
        model_configs = [
            # kimi_chat - 通用聊天配置
            {
                **base_config,
                "config_name": "kimi_chat",
                "generate_args": {"temperature": 0.7, "max_tokens": 2000},
            },
            # kimi_expert - 专家配置，使用32k模型，温度较低
            {
                **base_config,
                "config_name": "kimi_expert",
                "model_name": "moonshot-v1-32k",  # 使用32k上下文模型
                "generate_args": {"temperature": 0.5, "max_tokens": 4000},
            },
            # kimi_assistant - 助教配置，使用8k模型
            {
                **base_config,
                "config_name": "kimi_assistant",
                "model_name": "moonshot-v1-8k",  # 使用8k模型
                "generate_args": {"temperature": 0.8, "max_tokens": 2000},
            },
            # kimi_peer - 同伴配置，使用8k模型，温度较高
            {
                **base_config,
                "config_name": "kimi_peer",
                "model_name": "moonshot-v1-8k",  # 使用8k模型
                "generate_args": {"temperature": 0.9, "max_tokens": 2000},
            },
            # kimi_router - 路由智能体配置
            {
                **base_config,
                "config_name": "kimi_router",
                "model_name": "moonshot-v1-8k",
                "generate_args": {"temperature": 0.0, "max_tokens": 1000}, # 路由需要确定性，温度设为0
            }
        ]

        logger.info(f"动态构建了{len(model_configs)}个模型配置")
        return model_configs

    async def _create_agents(self) -> None:
        """创建智能体实例"""
        try:
            # 专家智能体 - 使用专门的专家配置
            self.agents["expert"] = DialogAgent(
                name="专家智能体",
                model_config_name="kimi_expert",  # 使用专家配置
                sys_prompt="你是一位资深的教育专家，擅长解答复杂的学术问题，提供深入的知识讲解和专业指导。你的回答应该准确、权威、有深度。",
            )

            # 助教智能体 - 使用专门的助教配置
            self.agents["assistant"] = DialogAgent(
                name="助教智能体",
                model_config_name="kimi_assistant",  # 使用助教配置
                sys_prompt="你是一位耐心的助教，擅长辅导学生学习，提供学习建议和答疑解惑。你的回答应该友善、易懂、有针对性。",
            )

            # 同伴智能体 - 使用专门的同伴配置
            self.agents["peer"] = DialogAgent(
                name="同伴智能体",
                model_config_name="kimi_peer",  # 使用同伴配置
                sys_prompt="你是一位学习伙伴，以同龄人的身份与学生交流，分享学习经验和心得。你的回答应该亲切、平等、富有共鸣。",
            )

            # 路由智能体 - 使用ReActAgentV2
            self.agents["router"] = ReActAgentV2(
                name="路由智能体",
                model_config_name="kimi_router",
                service_toolkit=ServiceToolkit(),  # 为ReActAgentV2提供ServiceToolkit实例
                # 注意：以下提示词中的花括号使用双花括号进行转义，避免 str.format 将其识别为占位符导致 KeyError
                sys_prompt="""你是一个智能路由专家，负责根据用户输入和对话历史，精确决定下一个发言的智能体。

**核心职责：**
1. 分析用户问题的复杂度和性质
2. 评估对话历史和上下文
3. 选择最适合的智能体类型

**智能体选择标准：**
- **expert**: 复杂学术问题、理论解释、深度分析
- **assistant**: 学习指导、练习辅导、方法建议  
- **peer**: 经验分享、情感支持、同龄交流

**响应格式要求：**
必须严格返回JSON格式：{{"agent": "智能体类型", "reason": "选择理由"}}

**停止信号支持：**
- 当对话自然结束时，返回：{{"agent": "STOP", "reason": "对话已完成"}}
- 识别停止关键词："再见"、"谢谢"、"结束"、"够了"

**对话轮次规则：**
- 避免同一智能体连续发言超过2轮；若确有必要（如用户明确要求或上下文强依赖），必须在reason中说明原因。

**示例：**
用户问"量子物理的基本原理是什么？"
返回：{{"agent": "expert", "reason": "需要专业的理论知识解释"}}

请确保响应格式正确，不要添加任何JSON之外的内容。""",
            )

            logger.info("智能体创建完成")

        except Exception as e:
            logger.error(f"智能体创建失败: {e}")
            raise

    def get_agent(self, agent_type: str) -> Optional[DialogAgent]:
        """获取指定类型的智能体"""
        if not self.initialized:
            logger.warning("AgentScope尚未初始化")
            return None

        return self.agents.get(agent_type)

    async def chat_with_agent(self, agent_type: str, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """与指定智能体对话"""
        agent = self.get_agent(agent_type)
        if not agent:
            raise ValueError(f"未找到智能体类型: {agent_type}")

        try:
            # 构建消息
            msg = Msg(name="user", content=message, role="user")

            # 如果有上下文信息，添加到消息中
            if context:
                context_str = f"\n\n上下文信息:\n{json.dumps(context, ensure_ascii=False, indent=2)}"
                msg.content += context_str

            # 获取智能体响应
            response = agent(msg)

            return response.content if hasattr(response, "content") else str(response)

        except Exception as e:
            logger.error(f"智能体对话失败: {e}")
            raise

    async def cleanup(self) -> None:
        """清理资源"""
        try:
            self.agents.clear()
            self.initialized = False
            logger.info("AgentScope资源清理完成")
        except Exception as e:
            logger.error(f"资源清理失败: {e}")


# 全局智能体管理器实例
agent_manager = AgentManager()


def get_agent_manager() -> AgentManager:
    """获取智能体管理器实例"""
    return agent_manager