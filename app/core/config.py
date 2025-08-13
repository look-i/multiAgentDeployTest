# 系统配置管理
# System Configuration Management

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = Field(default="智教魔方 AI教育系统", env="APP_NAME")
    app_description: str = Field(default="智教魔方 - 广东省中小学AI自学辅导助教系统", env="APP_DESCRIPTION")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # API配置
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Moonshot API配置
    moonshot_api_key: str = Field(..., env="MOONSHOT_API_KEY")
    moonshot_base_url: str = Field(default="https://api.moonshot.cn/v1", env="MOONSHOT_BASE_URL")
    moonshot_model: str = Field(default="kimi-k2-0711-preview", env="MOONSHOT_MODEL")
    
    # 安全配置（必须通过环境变量注入，生产环境请使用足够随机的字符串）
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS配置
    allowed_origins: list = Field(default=["*"], env="ALLOWED_ORIGINS")
    allowed_methods: list = Field(default=["*"], env="ALLOWED_METHODS")
    allowed_headers: list = Field(default=["*"], env="ALLOWED_HEADERS")
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    
    # AgentScope配置
    agentscope_model_config_path: str = Field(default="config/model_configs.json", env="AGENTSCOPE_MODEL_CONFIG_PATH")
    agentscope_logging_level: str = Field(default="INFO", env="AGENTSCOPE_LOGGING_LEVEL")
    
    # 个性化学习配置
    learning_style_weights: dict = Field(
        default={
            "visual": 0.25,
            "auditory": 0.25,
            "reading": 0.25,
            "kinesthetic": 0.25
        },
        env="LEARNING_STYLE_WEIGHTS"
    )
    
    # 认知负荷阈值
    cognitive_load_threshold: float = Field(default=0.7, env="COGNITIVE_LOAD_THRESHOLD")
    
    # 系统监控配置
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

# 全局配置实例
settings = Settings()

# 获取配置的便捷函数
def get_settings() -> Settings:
    """获取应用配置"""
    return settings