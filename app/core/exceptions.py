# 自定义异常类
# Custom Exception Classes

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class EduCubeException(Exception):
    """智教魔方基础异常类"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AgentScopeInitializationError(EduCubeException):
    """AgentScope初始化异常"""

    pass


class AgentNotFoundError(EduCubeException):
    """智能体未找到异常"""

    pass


class AgentCommunicationError(EduCubeException):
    """智能体通信异常"""

    pass


class PersonalizationServiceError(EduCubeException):
    """个性化服务异常"""

    pass


class LearningAnalyticsError(EduCubeException):
    """学习分析服务异常"""

    pass


class AnalyticsServiceError(EduCubeException):
    """分析服务异常"""

    pass


class DeepLearningServiceError(EduCubeException):
    """深度学习服务异常"""

    pass


class ConfigurationError(EduCubeException):
    """配置错误异常"""

    pass


class ValidationError(EduCubeException):
    """数据验证异常"""

    pass


class APIKeyError(EduCubeException):
    """API密钥错误异常"""

    pass


class ModelConfigError(EduCubeException):
    """模型配置错误异常"""

    pass


# HTTP异常类
class HTTPBadRequestException(HTTPException):
    """HTTP 400 错误请求异常"""

    def __init__(self, detail: str = "请求参数错误"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class HTTPUnauthorizedException(HTTPException):
    """HTTP 401 未授权异常"""

    def __init__(self, detail: str = "未授权访问"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class HTTPForbiddenException(HTTPException):
    """HTTP 403 禁止访问异常"""

    def __init__(self, detail: str = "禁止访问"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class HTTPNotFoundException(HTTPException):
    """HTTP 404 未找到异常"""

    def __init__(self, detail: str = "资源未找到"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class HTTPInternalServerErrorException(HTTPException):
    """HTTP 500 内部服务器错误异常"""

    def __init__(self, detail: str = "内部服务器错误"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class HTTPServiceUnavailableException(HTTPException):
    """HTTP 503 服务不可用异常"""

    def __init__(self, detail: str = "服务暂时不可用"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


# 异常处理工具函数
def handle_agentscope_error(error: Exception) -> EduCubeException:
    """处理AgentScope相关错误"""
    if "initialization" in str(error).lower():
        return AgentScopeInitializationError(f"AgentScope初始化失败: {str(error)}")
    elif "agent" in str(error).lower() and "not found" in str(error).lower():
        return AgentNotFoundError(f"智能体未找到: {str(error)}")
    else:
        return AgentCommunicationError(f"智能体通信错误: {str(error)}")


def handle_api_key_error(error: Exception) -> APIKeyError:
    """处理API密钥相关错误"""
    return APIKeyError(f"API密钥错误: {str(error)}")


def handle_model_config_error(error: Exception) -> ModelConfigError:
    """处理模型配置相关错误"""
    return ModelConfigError(f"模型配置错误: {str(error)}")


def handle_validation_error(error: Exception) -> ValidationError:
    """处理数据验证相关错误"""
    return ValidationError(f"数据验证失败: {str(error)}")
