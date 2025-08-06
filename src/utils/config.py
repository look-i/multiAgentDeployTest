# 导入os和dotenv库，用于处理环境变量
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 从环境变量中获取MOONSHOT_API_KEY
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")

# 检查API密钥是否存在，如果不存在则抛出异常
if not MOONSHOT_API_KEY:
    raise ValueError("未找到环境变量 MOONSHOT_API_KEY，请在 .env 文件中或操作系统环境中设置。")

# 定义模型配置
MODEL_CONFIG = {
    "config_name": "kimi_k2_config",
    "model_type": "openai_chat",
    "model_name": "kimi-k2-0711-preview",
    "api_key": MOONSHOT_API_KEY,
    "max_length": 128000,
    "client_args": {
        "base_url": "https://api.moonshot.cn/v1"
    }
}