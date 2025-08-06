# 导入FastAPI模块
from fastapi import FastAPI

# 创建一个FastAPI应用实例
app = FastAPI()

# 定义一个根路由
@app.get("/")
async def root():
    """
    根路由，返回一个欢迎信息。
    """
    return {"message": "欢迎使用'启智AI'--广东省中小学AI自学辅导助教系统"}

# 导入pydantic的BaseModel用于定义请求体
from pydantic import BaseModel
# 从pipeline模块导入新的函数
from src.pipeline import run_pipeline, load_agents

# 在应用启动时加载智能体
@app.on_event("startup")
async def startup_event():
    """
    应用启动时执行的事件，用于加载和初始化智能体。
    """
    print("应用启动，开始加载智能体...")
    load_agents()
    print("智能体加载完成。")

# 定义请求体模型
class ChatRequest(BaseModel):
    user_input: str

# 定义聊天路由
@app.post("/chat")
async def chat_with_agents(request: ChatRequest):
    """
    接收用户输入，运行多智能体流程，并返回对话历史。
    """
    # 调用pipeline处理用户输入
    history = run_pipeline(request.user_input)
    
    # 将Msg对象转换为字典列表以便JSON序列化
    response_history = [msg.to_dict() for msg in history]
    
    return {"history": response_history}