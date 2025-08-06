# 导入agentscope和相关模块
from agentscope.message import Msg
from agentscope.pipelines import sequential_pipeline
from agentscope import msghub
from .utils.agent_factory import (
    init_agentscope,
    create_expert_agent,
    create_ta_agent,
    create_peer_agent,
    create_manager_agent,
)

# 全局变量，用于存储智能体实例
AGENTS = {}

def load_agents():
    """
    初始化AgentScope并加载所有智能体。
    这个函数应该在应用启动时被调用一次。
    """
    # 初始化AgentScope
    init_agentscope()

    # 创建并存储智能体实例
    AGENTS['manager'] = create_manager_agent()
    AGENTS['expert'] = create_expert_agent()
    AGENTS['ta'] = create_ta_agent()
    AGENTS['peer'] = create_peer_agent()

    print("所有智能体已成功加载。")

def run_pipeline(user_input: str):
    """
    使用预加载的智能体运行多智能体教学流程。

    Args:
        user_input (str): 用户的初始输入，即学习任务。

    Returns:
        list: 对话历史记录。
    """
    # 从全局变量中获取智能体
    manager = AGENTS.get('manager')
    expert = AGENTS.get('expert')
    ta = AGENTS.get('ta')
    peer = AGENTS.get('peer')

    if not all([manager, expert, ta, peer]):
        raise RuntimeError("智能体未被正确加载，请先调用 load_agents()。")

    # 定义参与者列表
    participants = [manager, expert, ta, peer]

    # 初始化对话历史
    history = []

    # 使用msghub创建一个聊天室
    with msghub(participants=participants) as hub:
        start_msg = Msg(name="user", content=user_input, role="user")
        history.append(start_msg)

        print(f"开始处理用户输入: {user_input[:50]}...")

        x = start_msg

        # 流程控制：专家 -> 助教 -> 同伴 -> 助教
        for agent in [expert, ta, peer, ta]:
            x = agent(x)
            # 注意：在生产环境中，过多的print会影响性能
            # print(f"{x.name}: {x.content}") 
            history.append(x)

        print("...处理结束")

    return history

# # 用于本地测试
# if __name__ == '__main__':
#     task = "请解释一下什么是'人工智能'，并举一个生活中的例子。"
#     history = run_pipeline(task)
#     print("\n--- 对话历史 ---")
#     for msg in history:
#         print(f"[{msg.name}]: {msg.content}")