# 日志配置管理
# Logging Configuration Management

import logging
import logging.config
import os
from pathlib import Path
from typing import Dict, Any

from app.core.config import get_settings

settings = get_settings()

# 新增：日志级别规范化工具函数，兼容小写字符串与数字字符串
# 功能说明：
# - 如果传入是整数，直接返回（如 10、20 等）
# - 如果是可转为整数的字符串，转为整数返回（如 "20" -> 20）
# - 如果是普通字符串，统一转为大写（如 "info" -> "INFO"）
# - 其他异常情况返回 "INFO" 作为兜底，避免启动报错
def normalize_level(level: Any) -> Any:
    try:
        if isinstance(level, int):
            return level
        if isinstance(level, str):
            s = level.strip()
            if s.isdigit():
                return int(s)
            return s.upper()
    except Exception:
        pass
    return "INFO"

def setup_logging() -> None:
    """设置应用日志配置"""
    
    # 确保日志目录存在
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # 规范化应用与 AgentScope 日志级别，避免不合法级别导致 dictConfig 报错
    app_level = normalize_level(settings.log_level)
    agentscope_level = normalize_level(settings.agentscope_logging_level)
    
    # 日志配置字典
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": app_level,  # 使用规范化后的级别
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": app_level,  # 使用规范化后的级别
                "formatter": "detailed",
                "filename": settings.log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8"
            }
        },
        "loggers": {
            "app": {
                "level": app_level,  # 使用规范化后的级别
                "handlers": ["console", "file"],
                "propagate": False
            },
            "agentscope": {
                "level": agentscope_level,  # 使用规范化后的级别
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",  # 保持内置组件级别为 INFO
                "handlers": ["console", "file"],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO",  # 保持内置组件级别为 INFO
                "handlers": ["console", "file"],
                "propagate": False
            }
        },
        "root": {
            "level": app_level,  # 使用规范化后的级别
            "handlers": ["console", "file"]
        }
    }
    
    # 应用日志配置
    logging.config.dictConfig(logging_config)

def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器"""
    return logging.getLogger(name)

# 应用日志记录器
app_logger = get_logger("app")
agentscope_logger = get_logger("agentscope")