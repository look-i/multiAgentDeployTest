#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智教魔方 - 广东省中小学AI自学辅导助教系统
主入口文件
"""

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import router as api_router
from app.core.agent_manager import AgentManager
from app.core.exceptions import (
    AgentCommunicationError,
    PersonalizationServiceError,
    ValidationError
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("🚀 启动智教魔方系统...")
    
    # 初始化AgentScope智能体管理器
    agent_manager = AgentManager()
    await agent_manager.initialize()
    app.state.agent_manager = agent_manager
    
    logger.info("✅ 智教魔方系统启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("🔄 正在关闭智教魔方系统...")
    await agent_manager.cleanup()
    logger.info("✅ 智教魔方系统已安全关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    # 设置日志
    setup_logging()
    
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加受信任主机中间件
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.claudebase.com"]
        )
    
    # 添加请求处理时间中间件
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # 注册路由
    app.include_router(api_router)
    
    # 全局异常处理
    @app.exception_handler(AgentCommunicationError)
    async def agent_communication_error_handler(request: Request, exc: AgentCommunicationError):
        logger.error(f"智能体通信异常: {exc.message}")
        return JSONResponse(
            status_code=500,
            content={"error": "agent_communication_error", "message": exc.message}
        )
    
    @app.exception_handler(PersonalizationServiceError)
    async def personalization_service_error_handler(request: Request, exc: PersonalizationServiceError):
        logger.error(f"个性化服务异常: {exc.message}")
        return JSONResponse(
            status_code=500,
            content={"error": "personalization_service_error", "message": exc.message}
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        logger.warning(f"参数验证异常: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={"error": "validation_error", "message": exc.message}
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "http_error", "message": exc.detail}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "message": "服务器内部错误"}
        )
    
    # 根路径
    @app.get("/")
    async def root():
        return {
            "message": "欢迎使用智教魔方 - 广东省中小学AI自学辅导助教系统",
            "version": settings.app_version,
            "docs": "/docs" if settings.debug else "文档已禁用",
            "status": "running"
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        reload_dirs=["app"],  # 只监控app目录的文件变化，避免AgentScope的runs目录触发重新加载
        log_level=settings.log_level.lower()
    )