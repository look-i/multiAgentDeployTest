# 使用官方的 Python 3.9 slim 版本作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 将依赖文件复制到工作目录
COPY requirements.txt .

# 安装依赖，使用清华大学镜像源以提高下载速度和稳定性
# --no-cache-dir 选项可以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 将项目代码复制到工作目录
COPY . .

# 暴露端口，腾讯云CloudBase默认检查80端口
EXPOSE 80

# 启动命令，将端口修改为80以匹配平台要求
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "80"]