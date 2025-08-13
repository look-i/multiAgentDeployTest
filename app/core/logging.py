# 日志配置管理
# Logging Configuration Management

import logging
import logging.config
import os
import sys
from pathlib import Path
from typing import Dict, Any

from app.core.config import get_settings

settings = get_settings()

def validate_log_level(level: str) -> str:
    """验证并规范化日志级别"""
    # 支持的标准日志级别
    valid_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    # 转换为大写并验证
    level = level.upper()
    if level in valid_levels:
        return level
    else:
        # 如果级别无效，默认使用 INFO
        print(f"警告: 无效的日志级别 '{level}'，将使用默认级别 'INFO'")
        return "INFO"

def setup_logging() -> None:
    """设置应用日志配置"""
    
    try:
        # 确保日志目录存在
        log_dir = Path(settings.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 验证和规范化日志级别
        app_log_level = validate_log_level(settings.log_level)
        agentscope_log_level = validate_log_level(settings.agentscope_logging_level)
        
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
                    "level": app_log_level,
                    "formatter": "default"
                    # 移除可能有问题的 stream 配置，使用默认的 sys.stderr
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": app_log_level,
                    "formatter": "detailed",
                    "filename": settings.log_file,
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf-8"
                }
            },
            "loggers": {
                "app": {
                    "level": app_log_level,
                    "handlers": ["console", "file"],
                    "propagate": False
                },
                "agentscope": {
                    "level": agentscope_log_level,
                    "handlers": ["console", "file"],
                    "propagate": False
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console", "file"],
                    "propagate": False
                },
                "fastapi": {
                    "level": "INFO",
                    "handlers": ["console", "file"],
                    "propagate": False
                }
            },
            "root": {
                "level": app_log_level,
                "handlers": ["console", "file"]
            }
        }
        
        # 应用日志配置
        logging.config.dictConfig(logging_config)
        
    except Exception as e:
        # 如果日志配置失败，使用简单的基本配置
        print(f"警告: 日志配置失败 ({e})，使用基本配置")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("logs/app.log", encoding="utf-8")
            ]
        )

def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器"""
    return logging.getLogger(name)

# 应用日志记录器
app_logger = get_logger("app")
agentscope_logger = get_logger("agentscope")