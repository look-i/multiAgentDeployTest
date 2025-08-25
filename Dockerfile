# 使用官方 Python 运行时作为基础镜像（与 requirements.txt 保持一致，兼容性更好）
FROM python:3.9-slim

# 设置容器内工作目录
WORKDIR /app

# 设置基础环境变量
# - PYTHONDONTWRITEBYTECODE: 禁止 Python 生成 .pyc 文件，减少无用 I/O
# - PYTHONUNBUFFERED: 关闭输出缓冲，日志更实时
# - PIP_NO_CACHE_DIR / PIP_DISABLE_PIP_VERSION_CHECK: 关闭 Pip 缓存与版本检查，镜像更小、构建更快
# - PORT/HOST: 默认云端常见端口与监听地址，可在运行时通过 -e 覆盖
# - UVICORN_WORKERS: Uvicorn 并发进程数，默认 1，可按需在运行时调整
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080 \
    HOST=0.0.0.0 \
    UVICORN_WORKERS=1

# 安装系统依赖
# - gcc/libssl-dev/libffi-dev/python3-dev: 保障部分依赖需要编译时能顺利安装（稳妥）
# - curl: 用于容器 HEALTHCHECK 健康检查
# 安装完成后清理 apt 缓存，减小镜像体积
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libssl-dev \
    libffi-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 仅复制依赖清单，利用 Docker 层缓存
COPY requirements.txt .

# 升级 pip 并安装 Python 依赖
# 使用清华源可提高国内网络环境下的下载安装成功率
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

# 仅复制运行后端所需的代码，避免把前端、Java 后端、历史运行产物等打进镜像
COPY app ./app
COPY config ./config
COPY main.py ./main.py

# 创建日志目录并创建非 root 账号运行进程以提升安全性
RUN mkdir -p logs && \
    useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

# 切换到非 root 用户
USER app

# 暴露容器内服务端口（默认 8080，可在 run 时映射到宿主机端口）
EXPOSE 8080

# 健康检查：访问系统健康检查接口，若失败则返回非 0 状态，便于平台探活
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT:-8080}/api/v1/system/health" || exit 1

# 使用 Uvicorn 工厂模式启动 FastAPI（main:create_app）
# 通过环境变量 PORT 和 UVICORN_WORKERS 控制端口与并发进程数
ENTRYPOINT ["sh", "-c"]
CMD ["uvicorn main:create_app --factory --host 0.0.0.0 --port ${PORT:-8080} --workers ${UVICORN_WORKERS:-1}"]