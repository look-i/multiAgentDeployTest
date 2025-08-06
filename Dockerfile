# 使用官方的 Python 3.9 slim 版本作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 将依赖文件复制到工作目录
COPY requirements.txt .

# 安装依赖
# --no-cache-dir 选项可以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 将项目代码复制到工作目录
COPY . .

# 暴露 FastAPI 应用运行的端口
EXPOSE 8000

# 定义容器启动时执行的命令
# 运行 uvicorn 服务器，并监听所有网络接口
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]