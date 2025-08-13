# 使用官方Python运行时作为基础镜像（与requirements.txt匹配）
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，包括云端部署默认配置
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080 \
    HOST=0.0.0.0

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 升级pip到最新版本
RUN pip install --upgrade pip

# 安装Python依赖，使用国内镜像源并增加重试机制
RUN pip install --no-cache-dir --retries 5 --timeout 300 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
    -r requirements.txt

# 复制项目文件
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 暴露端口 8080（使用非特权端口，适配非root用户）
EXPOSE 8080

# 启动命令
CMD ["python", "main.py"]