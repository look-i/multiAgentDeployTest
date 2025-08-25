# my-rule

1、 所有终端命令，请向我提供可直接粘贴运行的命令
2、 所有终端命令，由我自己手动执行
3、 智能体接入LLM的url地址为：https://api.moonshot.cn/v1
4、 LLM使用的api key为：sk-YnZ6AmSGHxyau9OHQJGpRmSBoLcMHQ8XrP5oPFfBz7dy4pVC（但是实际上是从环境变量读取）
5、 LLM模型为：kimi-k2-0711-preview
6、 AgentScope版本号为0.1.6，请按照最新版本的代码规范来写代码。如果你不知道或者不确定最新版本的代码规范，立即停止编码，并告知我，让我给你提供代码规范参考
7、 以下是部分代码规范示例：

一、简单多智能体对话，支持灵活的信息流控制和智能体间通信：
import os
from agentscope.agents import DialogAgent
from agentscope.message import Msg
from agentscope.pipelines import sequential_pipeline
from agentscope import msghub
import agentscope

# 从环境变量中读取API密钥，如果找不到则返回None
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
# 检查是否成功获取到API Key
if not MOONSHOT_API_KEY:
    raise ValueError("未找到环境变量 MOONSHOT_API_KEY，请确保已经正确设置。")
# 加载模型配置
agentscope.init(
    model_configs=[
        {
            "config_name": "kimi_k2_config",  # 自定义配置名
            "model_type": "openai_chat",
            "model_name": "kimi-k2-0711-preview",  # 或 kimi-k2-turbo-preview
            "api_key": MOONSHOT_API_KEY,
            "max_length": 128000,
            "client_args": {
                "base_url": "https://api.moonshot.cn/v1"
            }
        }
    ]
)

# 创建三个智能体
friday = DialogAgent(
    name="Friday",
    model_config_name="kimi_k2_config",
    sys_prompt="你是一个名为Friday的助手"
)

saturday = DialogAgent(
    name="Saturday",
    model_config_name="kimi_k2_config",
    sys_prompt="你是一个名为Saturday的助手"
)

sunday = DialogAgent(
    name="Sunday",
    model_config_name="kimi_k2_config",
    sys_prompt="你是一个名为Sunday的助手"
)

# 通过msghub创建一个聊天室，智能体的消息会广播给所有参与者
with msghub(
    participants=[friday, saturday, sunday],
    announcement=Msg("user", "从1开始数数，每次只报一个数字，不要说其他内容", "user"),  # 一个问候消息
) as hub:
    # 按顺序发言
    sequential_pipeline([friday, saturday, sunday], x=None)

二、轻松创建一个 ReAct 智能体，并装备工具和 MCP Server：
from agentscope.agents import ReActAgentV2, UserAgent
from agentscope.service import ServiceToolkit, execute_python_code
import agentscope
import os

# 从环境变量中读取API密钥，如果找不到则返回None
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
# 检查是否成功获取到API Key
if not MOONSHOT_API_KEY:
    raise ValueError("未找到环境变量 MOONSHOT_API_KEY，请确保已经正确设置。")
# 加载模型配置
agentscope.init(
    model_configs=[
        {
            "config_name": "kimi_k2_config",  # 自定义配置名
            "model_type": "openai_chat",
            "model_name": "kimi-k2-0711-preview",  # 或 kimi-k2-turbo-preview
            "api_key": MOONSHOT_API_KEY,
            "max_length": 128000,
            "client_args": {
                "base_url": "https://api.moonshot.cn/v1"
            }
        }
    ]
)

# 添加内置工具
toolkit = ServiceToolkit()
toolkit.add(execute_python_code)

# 连接到高德 MCP Server
toolkit.add_mcp_servers(
    {
        "mcpServers": {
            "amap-amap-sse": {
                "type": "sse",
                "url": "https://mcp.amap.com/sse?key=a6e8ec276a3d6451198557d165d795b5"
            }
        }
    }
)

# 创建一个 ReAct 智能体
agent = ReActAgentV2(
    name="Friday",
    model_config_name="kimi_k2_config",
    service_toolkit=toolkit,
    sys_prompt="你是一个名为Friday的AI助手。"
)
user_agent = UserAgent(name="user")

# 显式构建工作流程/对话
x = None
while x is None or x.content != "exit":
    x = agent(x)
    x = user_agent(x)

三、使用 Pydantic 的 BaseModel 轻松指定&切换结构化输出：
from operator import imod
from agentscope.agents import ReActAgentV2
from agentscope.service import ServiceToolkit
from agentscope.message import Msg
from pydantic import BaseModel, Field
from typing import Literal
import agentscope
import os

# 从环境变量中读取API密钥，如果找不到则返回None
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
# 检查是否成功获取到API Key
if not MOONSHOT_API_KEY:
    raise ValueError("未找到环境变量 MOONSHOT_API_KEY，请确保已经正确设置。")
# 加载模型配置
agentscope.init(
    model_configs=[
        {
            "config_name": "kimi_k2_config",  # 自定义配置名
            "model_type": "openai_chat",
            "model_name": "kimi-k2-0711-preview",  # 或 kimi-k2-turbo-preview
            "api_key": MOONSHOT_API_KEY,
            "max_length": 128000,
            "client_args": {
                "base_url": "https://api.moonshot.cn/v1"
            }
        }
    ]
)

# 创建一个推理-行动智能体
agent = ReActAgentV2(
    name="Friday",
    model_config_name="kimi_k2_config",
    service_toolkit=ServiceToolkit(),
    max_iters=20
)

class CvModel(BaseModel):
    name: str = Field(max_length=50, description="姓名")
    description: str = Field(max_length=200, description="简短描述")
    aget: int = Field(gt=0, le=120, description="年龄")

# class ChoiceModel(BaseModel):
#     choice: Literal["apple", "banana"]

# 使用`structured_model`字段指定结构化输出
res_msg = agent(
    Msg("user", "介绍下爱因斯坦", "user"),
    structured_model=CvModel
)
print(res_msg.metadata)

# 切换到不同的结构化输出
# res_msg = agent(
#     Msg("user", "选择一个水果", "user"),
#     structured_model=ChoiceModel
# )
# print(res_msg.metadata)

四、使用 AgentScope 轻松构建各种类型的智能体工作流，以 Routing 为例：
from agentscope.agents import ReActAgentV2
from agentscope.service import ServiceToolkit
from agentscope.message import Msg
from pydantic import BaseModel, Field
from typing import Literal, Union
import agentscope

# 从环境变量中读取API密钥，如果找不到则返回None
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
# 检查是否成功获取到API Key
if not MOONSHOT_API_KEY:
    raise ValueError("未找到环境变量 MOONSHOT_API_KEY，请确保已经正确设置。")
# 加载模型配置
agentscope.init(
    model_configs=[
        {
            "config_name": "kimi_k2_config",  # 自定义配置名
            "model_type": "openai_chat",
            "model_name": "kimi-k2-0711-preview",  # 或 kimi-k2-turbo-preview
            "api_key": MOONSHOT_API_KEY,
            "max_length": 128000,
            "client_args": {
                "base_url": "https://api.moonshot.cn/v1"
            }
        }
    ]
)

# Routing 智能体
routing_agent = ReActAgentV2(
    name="Routing",
    model_config_name="my_config",
    sys_prompt="你是一个路由智能体。你的目标是将用户查询路由到正确的后续任务",
    service_toolkit=ServiceToolkit()
)

# 使用结构化输出来指定路由结果
class RoutingChoice(BaseModel):
    your_choice: Literal[
        'Content Generation',
        'Programming',
        'Information Retrieval',
        None
    ] = Field(description="选择正确的后续任务，如果任务太简单或没有合适的任务，选择`None`")
    task_description: Union[str, None] = Field(description="任务描述", default=None)

res_msg = routing_agent(
    Msg("user", "帮我写一首诗", "user"),
    structured_model=RoutingChoice
)

# 执行后续任务
if res_msg.metadata["your_choice"] == "Content Generation":
    ...
elif res_msg.metadata["your_choice"] == "Programming":
    ...
elif res_msg.metadata["your_choice"] == "Information Retrieval":
    ...
else:
    ...

五、使用to_dist函数在分布式模式下运行智能体：
from agentscope.agents import DialogAgent
from agentscope.message import Msg
import agentscope

# 从环境变量中读取API密钥，如果找不到则返回None
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
# 检查是否成功获取到API Key
if not MOONSHOT_API_KEY:
    raise ValueError("未找到环境变量 MOONSHOT_API_KEY，请确保已经正确设置。")
# 加载模型配置
agentscope.init(
    model_configs=[
        {
            "config_name": "kimi_k2_config",  # 自定义配置名
            "model_type": "openai_chat",
            "model_name": "kimi-k2-0711-preview",  # 或 kimi-k2-turbo-preview
            "api_key": MOONSHOT_API_KEY,
            "max_length": 128000,
            "client_args": {
                "base_url": "https://api.moonshot.cn/v1"
            }
        }
    ]
)

# 使用`to_dist()`在分布式模式下运行智能体
agent1 = DialogAgent(
    name="Saturday",
    model_config_name="my_config"
).to_dist()

agent2 = DialogAgent(
    name="Sunday",
    model_config_name="my_config"
).to_dist()

# 两个智能体将并行运行
agent1(Msg("user", "执行任务1...", "user"))
agent2(Msg("user", "执行任务2...", "user"))

六、AgentScope 提供了一个本地可视化和监控工具，AgentScope Studio，工具调用，模型 API 调用，Token 使用轻松追踪，一目了然：
将 Python 应用连接到 AgentScope Studio：
import agentscope

# 将应用程序连接到 AgentScope Studio
agentscope.init(
  model_configs = {
    "config_name": "my_config",
    "model_type": "dashscope_chat",
    "model_name": "qwen_max",
  },
  studio_url="http://localhost:3000", # AgentScope Studio 的 URL
)

# ...

8、项目启动时，创建一个“操作跟踪文档”，在此以后，每次对话前需要阅读“操作跟踪文档”再进行思考
9、前端文件夹路径是E:\EduCube Nexus\Project\multi_agent\frontend\zjmf-front
10、后端文件夹路径是E:\EduCube Nexus\Project\multi_agent\backend