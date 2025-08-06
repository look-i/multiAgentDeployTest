# -*- coding: utf-8 -*-

from agentscope.agents import AgentBase
from agentscope.message import Msg

class ManagerAgent(AgentBase):
    """一个不调用LLM的简单管理器智能体，用于控制对话流程。"""

    def __init__(self) -> None:
        # 调用父类的构造函数，并传入一个独特的名称
        super().__init__(name="Manager")

    def reply(self, x: Msg) -> Msg:
        # 这个智能体不生成新内容，只是作为一个流程控制器。
        # 在实际应用中，它的逻辑会更复杂，例如根据输入决定下一个发言者。
        # 这里我们只是简单地将消息传递下去，具体的流程控制在pipeline中实现。
        pass