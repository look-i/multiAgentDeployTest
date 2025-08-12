# 智教魔方 (EduCube Nexus)

基于 FastAPI + AgentScope 的多智能体 AI 教育后端服务系统

## 项目简介

智教魔方是一个创新的AI教育平台，采用完全无状态架构设计，通过多智能体协作为学习者提供个性化的学习体验。系统集成了先进的学习风格识别、认知负荷评估和个性化内容生成技术。

## 核心特性

### 🤖 多智能体架构 (已实现基础功能)
- **专家智能体**: 提供权威的学术指导和深度知识讲解。
- **助教智能体**: 提供耐心的学习辅导和答疑解惑。
- **同伴智能体**: 以同龄人身份提供学习交流和经验分享。
- **智能路由**: 可根据问题类型（理论、操作、一般性问题）将请求路由给最合适的智能体。

### 🎯 个性化学习引擎 (接口已定义，逻辑待实现)
- API接口已定义，可接收学习风格、认知状态等参数。
- **注意**: 后端服务当前为模拟实现，尚未集成真正的VARK分析和认知负荷评估模型。

### 📊 智能学习分析 (接口已定义，逻辑待实现)
- API接口已定义，可接收分析请求。
- **注意**: 后端服务当前为模拟实现，尚未集成真实的数据分析逻辑。

### 🚀 深度学习模式 (接口已定义，逻辑待实现)
- API接口已定义，可接收深度学习请求。
- **注意**: 后端服务当前为模拟实现，尚未实现多智能体协作的结构化学习流程。

## 技术架构

### 后端技术栈
- **FastAPI**: 高性能异步Web框架
- **AgentScope**: 多智能体协作引擎
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI服务器
- **Python 3.8+**: 核心开发语言

### AI模型集成
- **Kimi API**: 月之暗面大语言模型
- **多模型配置**: 支持不同场景的模型选择
- **智能体个性化**: 每个智能体独特的提示词和参数

### 架构设计原则
- **完全无状态**: 所有状态信息由前端管理和传递
- **微服务化**: 模块化设计，易于扩展和维护
- **高并发支持**: 异步处理，支持大量并发请求
- **可观测性**: 完整的日志记录和监控体系

## API 接口

### 核心接口列表

| 接口路径 | 方法 | 功能描述 |
|---------|------|----------|
| `/api/v1/agent/chat` | POST | 智能体对话交流 |
| `/api/v1/content/personalized` | POST | 个性化内容生成 |
| `/api/v1/learning/path` | POST | 个性化学习路径 |
| `/api/v1/learning/deep-mode` | POST | 深度学习模式 |
| `/api/v1/analytics/learning` | POST | 学习数据分析 |
| `/api/v1/qa/intelligent` | POST | 智能问答服务 |
| `/api/v1/system/health` | GET | 系统健康检查 |
| `/` | GET | 服务状态检查 |

### 请求示例

#### 智能体对话
```json
{
  "message": "请解释一下机器学习的基本概念",
  "agent_type": "expert",
  "context": {
    "user_id": "user123",
    "session_id": "session456",
    "learning_style": {
      "visual": 0.7,
      "auditory": 0.3,
      "reading": 0.5,
      "kinesthetic": 0.2
    },
    "cognitive_state": {
      "cognitive_load": 0.5,
      "attention_level": 0.8,
      "comprehension_rate": 0.7,
      "learning_progress": 0.6
    },
    "difficulty_level": 3
  }
}
```

#### 个性化内容生成
```json
{
  "topic": "线性代数",
  "content_type": "explanation",
  "context": {
    "user_id": "user123",
    "session_id": "session456",
    "learning_style": {
      "visual": 0.8,
      "auditory": 0.2,
      "reading": 0.6,
      "kinesthetic": 0.3
    },
    "cognitive_state": {
      "cognitive_load": 0.4,
      "attention_level": 0.9,
      "comprehension_rate": 0.8,
      "learning_progress": 0.5
    },
    "difficulty_level": 3
  }
}
```

## 快速开始

### 环境要求
- Python 3.8+
- pip 或 poetry
- Kimi API Key

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd EduCube-Nexus
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置信息
```

4. **启动服务**
```bash
python main.py
```

### 环境变量配置

创建 `.env` 文件并配置以下变量：

```env
# Kimi API 配置
MOONSHOT_API_KEY=your_kimi_api_key_here
KIMI_API_BASE=https://api.moonshot.cn/v1
KIMI_MODEL=moonshot-v1-8k

# 应用配置
APP_NAME=智教魔方 AI教育系统
DEBUG=false
HOST=0.0.0.0
PORT=8000

# 安全配置
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Docker 部署

```bash
# 构建镜像
docker build -t educube-nexus .

# 运行容器
docker run -d -p 8000:8000 --env-file .env educube-nexus
```

## 开发指南

### 项目结构

```
EduCube-Nexus/
├── app/                    # 应用核心代码
│   ├── api/               # API路由定义
│   ├── core/              # 核心配置和管理
│   ├── models/            # 数据模型定义
│   ├── services/          # 业务逻辑服务
│   ├── agents/            # 智能体定义
│   └── utils/             # 工具函数
├── config/                # 配置文件
├── tests/                 # 测试代码
├── logs/                  # 日志文件
├── main.py               # 应用入口
├── requirements.txt      # 依赖列表
└── README.md            # 项目文档
```

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 使用类型注解提高代码可读性
- 编写完整的文档字符串
- 保持函数和类的单一职责

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_main.py

# 生成测试覆盖率报告
pytest --cov=app tests/
```

## 部署指南

### 生产环境部署

1. **使用 Gunicorn + Uvicorn**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **使用 Nginx 反向代理**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **使用 Supervisor 进程管理**
```ini
[program:educube-nexus]
command=gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
directory=/path/to/EduCube-Nexus
autostart=true
autorestart=true
user=www-data
```

### 监控和日志

- 应用日志存储在 `logs/app.log`
- 支持日志轮转，避免文件过大
- 可集成 ELK Stack 进行日志分析
- 支持 Prometheus 指标收集

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系我们

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 邮箱: contact@educube-nexus.com

## 更新日志

### v1.0.0 (2024-01-XX)
- 🎉 初始版本发布
- ✨ 多智能体对话系统
- ✨ 个性化学习引擎
- ✨ 深度学习模式
- ✨ 学习分析服务
- ✨ 智能问答系统
- 📚 完整的API文档
- 🧪 单元测试覆盖

---

**智教魔方 - 让AI教育更智能，让学习更个