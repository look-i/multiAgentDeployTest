# 导入agentscope和相关模块
import agentscope
from .config import MODEL_CONFIG

# 初始化AgentScope
def init_agentscope():
    """
    使用配置文件中的设置初始化AgentScope。
    """
    agentscope.init(model_configs=[MODEL_CONFIG])

# 导入所需智能体
from agentscope.agents import DialogAgent
from ..agents.manager_agent import ManagerAgent
from .config import MODEL_CONFIG

# 定义专家智能体的系统提示
EXPERT_PROMPT = (
    "你是一位AI教育专家，你的名字叫'智多星'。"
    "你的核心任务是："
    "1. 根据用户提出的学习任务，制定清晰、具体的任务目标和评价标准。"
    "2. 将专业的评价标准，转化为中小学生容易理解、可以用来自己评价的'学习检查单'。"
    "你的回答必须权威、严谨，同时又要充满鼓励性。"
)

# 定义助教智能体的系统提示
TA_PROMPT = (
    "你是一位充满耐心和智慧的AI助教，你的名字叫'启思'。"
    "你的任务是协助学习者完成任务："
    "1. 将专家制定的复杂任务，分解成2-3个简单的步骤。"
    "2. 根据任务需要，推荐合适的学习资源，比如视频或在线工具。"
    "3. 在同伴智能体完成后，根据专家给出的'学习检查单'进行评价，要做到有理有据。"
    "4. 多使用启发式提问，引导学习者深度思考，而不是直接给出答案。"
)

# 定义同伴智能体的系统提示
PEER_PROMPT = (
    "你是一个正在学习AI的同学，你的名字叫'思学'。"
    "你的任务是模拟一个初学者的学习过程："
    "1. 在解决问题时，要大声说出你的'思考过程'，让大家知道你是怎么想的。"
    "2. 你可以犯一些初学者常犯的错误，但之后要能自己发现并改正，并解释为什么错了，以及如何改正。"
    "3. 你的表现要像一个真实的学生，有好奇心，也会有困惑。"
)

def create_expert_agent() -> DialogAgent:
    """
    创建一个专家智能体。
    """
    return DialogAgent(
        name="ExpertAgent",
        sys_prompt=EXPERT_PROMPT,
        model_config_name=MODEL_CONFIG["config_name"],
    )

def create_ta_agent() -> DialogAgent:
    """
    创建一个助教智能体。
    """
    return DialogAgent(
        name="TAAgent",
        sys_prompt=TA_PROMPT,
        model_config_name=MODEL_CONFIG["config_name"],
    )

def create_peer_agent() -> DialogAgent:
    """
    创建一个同伴智能体。
    """
    return DialogAgent(
        name="PeerAgent",
        sys_prompt=PEER_PROMPT,
        model_config_name=MODEL_CONFIG["config_name"],
    )

def create_manager_agent() -> ManagerAgent:
    """
    创建一个管理器智能体。
    """
    return ManagerAgent()