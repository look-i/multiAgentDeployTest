# 学习分析服务
# Learning Analytics Service

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.models.schemas import (
    LearningContext, LearningAnalyticsRequest, LearningAnalyticsResponse
)
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.agent_manager import get_agent_manager

settings = get_settings()
logger = get_logger("app.analytics")

class AnalyticsService:
    """学习分析服务"""
    
    def __init__(self):
        self.agent_manager = get_agent_manager()
    
    async def analyze_learning_data(
        self, 
        request: LearningAnalyticsRequest
    ) -> LearningAnalyticsResponse:
        """分析学习数据"""
        try:
            logger.info(f"开始学习分析: {request.user_id} - {request.analysis_type}")
            
            # 根据分析类型选择不同的分析方法
            if request.analysis_type == "progress":
                result = await self._analyze_learning_progress(request)
            elif request.analysis_type == "performance":
                result = await self._analyze_learning_performance(request)
            elif request.analysis_type == "behavior":
                result = await self._analyze_learning_behavior(request)
            else:
                raise ValueError(f"不支持的分析类型: {request.analysis_type}")
            
            return LearningAnalyticsResponse(
                success=True,
                message="学习分析完成",
                data=result,
                analysis_type=request.analysis_type,
                metrics=result["metrics"],
                insights=result["insights"],
                recommendations=result["recommendations"]
            )
            
        except Exception as e:
            logger.error(f"学习分析失败: {e}")
            return LearningAnalyticsResponse(
                success=False,
                message=f"学习分析失败: {str(e)}",
                analysis_type=request.analysis_type,
                metrics={},
                insights=[],
                recommendations=[]
            )
    
    async def _analyze_learning_progress(self, request: LearningAnalyticsRequest) -> Dict[str, Any]:
        """分析学习进度"""
        
        # 模拟学习进度数据（实际应用中应从数据库获取）
        progress_data = self._simulate_progress_data(request.user_id)
        
        # 计算进度指标
        metrics = {
            "overall_progress": progress_data["completion_rate"],
            "weekly_progress": progress_data["weekly_completion"],
            "learning_velocity": progress_data["topics_per_week"],
            "consistency_score": progress_data["consistency"],
            "milestone_achievements": progress_data["milestones_completed"],
            "time_spent_hours": progress_data["total_hours"],
            "active_days": progress_data["active_days"]
        }
        
        # 生成学习洞察
        insights = await self._generate_progress_insights(metrics, request.user_id)
        
        # 生成改进建议
        recommendations = await self._generate_progress_recommendations(metrics, request.user_id)
        
        return {
            "metrics": metrics,
            "insights": insights,
            "recommendations": recommendations,
            "trend_analysis": self._analyze_progress_trends(progress_data),
            "comparative_analysis": self._compare_with_peers(progress_data)
        }
    
    async def _analyze_learning_performance(self, request: LearningAnalyticsRequest) -> Dict[str, Any]:
        """分析学习表现"""
        
        # 模拟学习表现数据
        performance_data = self._simulate_performance_data(request.user_id)
        
        # 计算表现指标
        metrics = {
            "average_score": performance_data["avg_score"],
            "score_trend": performance_data["score_trend"],
            "accuracy_rate": performance_data["accuracy"],
            "improvement_rate": performance_data["improvement"],
            "strong_areas": performance_data["strengths"],
            "weak_areas": performance_data["weaknesses"],
            "difficulty_adaptation": performance_data["difficulty_match"],
            "response_time": performance_data["avg_response_time"]
        }
        
        # 生成表现洞察
        insights = await self._generate_performance_insights(metrics, request.user_id)
        
        # 生成改进建议
        recommendations = await self._generate_performance_recommendations(metrics, request.user_id)
        
        return {
            "metrics": metrics,
            "insights": insights,
            "recommendations": recommendations,
            "skill_analysis": self._analyze_skill_mastery(performance_data),
            "learning_efficiency": self._calculate_learning_efficiency(performance_data)
        }
    
    async def _analyze_learning_behavior(self, request: LearningAnalyticsRequest) -> Dict[str, Any]:
        """分析学习行为"""
        
        # 模拟学习行为数据
        behavior_data = self._simulate_behavior_data(request.user_id)
        
        # 计算行为指标
        metrics = {
            "session_frequency": behavior_data["sessions_per_week"],
            "session_duration": behavior_data["avg_session_duration"],
            "engagement_level": behavior_data["engagement_score"],
            "interaction_patterns": behavior_data["interaction_types"],
            "peak_learning_times": behavior_data["peak_hours"],
            "resource_usage": behavior_data["resource_preferences"],
            "help_seeking_frequency": behavior_data["help_requests"],
            "self_regulation": behavior_data["self_regulation_score"]
        }
        
        # 生成行为洞察
        insights = await self._generate_behavior_insights(metrics, request.user_id)
        
        # 生成改进建议
        recommendations = await self._generate_behavior_recommendations(metrics, request.user_id)
        
        return {
            "metrics": metrics,
            "insights": insights,
            "recommendations": recommendations,
            "learning_patterns": self._identify_learning_patterns(behavior_data),
            "optimization_opportunities": self._identify_optimization_opportunities(behavior_data)
        }
    
    def _simulate_progress_data(self, user_id: str) -> Dict[str, Any]:
        """模拟学习进度数据"""
        import random
        
        return {
            "completion_rate": round(random.uniform(0.3, 0.9), 2),
            "weekly_completion": round(random.uniform(0.1, 0.3), 2),
            "topics_per_week": round(random.uniform(2, 8), 1),
            "consistency": round(random.uniform(0.4, 0.9), 2),
            "milestones_completed": random.randint(3, 12),
            "total_hours": round(random.uniform(20, 100), 1),
            "active_days": random.randint(15, 45)
        }
    
    def _simulate_performance_data(self, user_id: str) -> Dict[str, Any]:
        """模拟学习表现数据"""
        import random
        
        return {
            "avg_score": round(random.uniform(60, 95), 1),
            "score_trend": "improving" if random.random() > 0.3 else "stable",
            "accuracy": round(random.uniform(0.7, 0.95), 2),
            "improvement": round(random.uniform(0.05, 0.25), 2),
            "strengths": random.sample(["概念理解", "应用能力", "分析思维", "创新思维"], 2),
            "weaknesses": random.sample(["记忆保持", "细节注意", "时间管理", "表达能力"], 1),
            "difficulty_match": round(random.uniform(0.6, 0.9), 2),
            "avg_response_time": round(random.uniform(30, 120), 1)
        }
    
    def _simulate_behavior_data(self, user_id: str) -> Dict[str, Any]:
        """模拟学习行为数据"""
        import random
        
        return {
            "sessions_per_week": round(random.uniform(3, 7), 1),
            "avg_session_duration": round(random.uniform(25, 60), 1),
            "engagement_score": round(random.uniform(0.6, 0.9), 2),
            "interaction_types": {
                "reading": round(random.uniform(0.3, 0.5), 2),
                "practicing": round(random.uniform(0.2, 0.4), 2),
                "discussing": round(random.uniform(0.1, 0.3), 2)
            },
            "peak_hours": random.sample(["9-11", "14-16", "19-21"], 2),
            "resource_preferences": {
                "text": round(random.uniform(0.2, 0.4), 2),
                "video": round(random.uniform(0.3, 0.5), 2),
                "interactive": round(random.uniform(0.2, 0.4), 2)
            },
            "help_requests": random.randint(2, 10),
            "self_regulation_score": round(random.uniform(0.5, 0.8), 2)
        }
    
    async def _generate_progress_insights(self, metrics: Dict[str, Any], user_id: str) -> List[str]:
        """生成学习进度洞察"""
        
        insights_prompt = f"""
基于以下学习进度数据，请生成3-5个关键洞察：

进度指标：
- 总体完成率：{metrics['overall_progress']:.1%}
- 周完成率：{metrics['weekly_progress']:.1%}
- 学习速度：{metrics['learning_velocity']}个主题/周
- 学习一致性：{metrics['consistency_score']:.1%}
- 里程碑完成：{metrics['milestone_achievements']}个
- 学习时长：{metrics['time_spent_hours']}小时
- 活跃天数：{metrics['active_days']}天

请分析学习者的进度特点，识别优势和需要关注的方面。每个洞察应该简洁明了，基于数据事实。
"""
        
        try:
            insights_text = await self.agent_manager.chat_with_agent(
                agent_type="expert",
                message=insights_prompt
            )
            
            # 解析洞察列表
            insights = self._parse_insights_list(insights_text)
            return insights[:5]  # 最多返回5个洞察
            
        except Exception as e:
            logger.error(f"进度洞察生成失败: {e}")
            return [
                f"学习完成率为{metrics['overall_progress']:.1%}，{'表现良好' if metrics['overall_progress'] > 0.7 else '需要加强'}",
                f"学习一致性为{metrics['consistency_score']:.1%}，{'保持稳定' if metrics['consistency_score'] > 0.6 else '波动较大'}"
            ]
    
    async def _generate_performance_insights(self, metrics: Dict[str, Any], user_id: str) -> List[str]:
        """生成学习表现洞察"""
        
        insights_prompt = f"""
基于以下学习表现数据，请生成3-5个关键洞察：

表现指标：
- 平均得分：{metrics['average_score']}
- 得分趋势：{metrics['score_trend']}
- 准确率：{metrics['accuracy_rate']:.1%}
- 改进幅度：{metrics['improvement_rate']:.1%}
- 优势领域：{', '.join(metrics['strong_areas'])}
- 薄弱环节：{', '.join(metrics['weak_areas'])}
- 难度适配度：{metrics['difficulty_adaptation']:.1%}
- 平均响应时间：{metrics['response_time']}秒

请分析学习者的表现特点，识别学习效果和改进空间。
"""
        
        try:
            insights_text = await self.agent_manager.chat_with_agent(
                agent_type="expert",
                message=insights_prompt
            )
            
            insights = self._parse_insights_list(insights_text)
            return insights[:5]
            
        except Exception as e:
            logger.error(f"表现洞察生成失败: {e}")
            return [
                f"平均得分{metrics['average_score']}分，{'表现优秀' if metrics['average_score'] > 80 else '有提升空间'}",
                f"在{', '.join(metrics['strong_areas'])}方面表现突出"
            ]
    
    async def _generate_behavior_insights(self, metrics: Dict[str, Any], user_id: str) -> List[str]:
        """生成学习行为洞察"""
        
        insights_prompt = f"""
基于以下学习行为数据，请生成3-5个关键洞察：

行为指标：
- 学习频率：{metrics['session_frequency']}次/周
- 平均学习时长：{metrics['session_duration']}分钟/次
- 参与度：{metrics['engagement_level']:.1%}
- 高峰学习时段：{', '.join(metrics['peak_learning_times'])}
- 求助频率：{metrics['help_seeking_frequency']}次
- 自我调节能力：{metrics['self_regulation']:.1%}

请分析学习者的行为模式，识别学习习惯的特点。
"""
        
        try:
            insights_text = await self.agent_manager.chat_with_agent(
                agent_type="assistant",
                message=insights_prompt
            )
            
            insights = self._parse_insights_list(insights_text)
            return insights[:5]
            
        except Exception as e:
            logger.error(f"行为洞察生成失败: {e}")
            return [
                f"学习频率为{metrics['session_frequency']}次/周，{'规律性良好' if metrics['session_frequency'] >= 4 else '需要提高规律性'}",
                f"参与度为{metrics['engagement_level']:.1%}，{'积极主动' if metrics['engagement_level'] > 0.7 else '需要激发兴趣'}"
            ]
    
    async def _generate_progress_recommendations(self, metrics: Dict[str, Any], user_id: str) -> List[str]:
        """生成进度改进建议"""
        
        recommendations = []
        
        if metrics["overall_progress"] < 0.5:
            recommendations.append("建议制定更明确的学习计划，设置阶段性目标")
        
        if metrics["consistency_score"] < 0.6:
            recommendations.append("建议建立固定的学习时间，提高学习的规律性")
        
        if metrics["learning_velocity"] < 3:
            recommendations.append("可以适当增加学习强度，提高学习效率")
        
        if metrics["active_days"] < 20:
            recommendations.append("建议增加学习频率，保持持续的学习状态")
        
        return recommendations[:4] if recommendations else ["继续保持当前的学习节奏"]
    
    async def _generate_performance_recommendations(self, metrics: Dict[str, Any], user_id: str) -> List[str]:
        """生成表现改进建议"""
        
        recommendations = []
        
        if metrics["average_score"] < 70:
            recommendations.append("建议加强基础知识的学习和巩固")
        
        if metrics["accuracy_rate"] < 0.8:
            recommendations.append("建议放慢学习节奏，注重理解质量")
        
        if len(metrics["weak_areas"]) > 0:
            weak_area = metrics["weak_areas"][0]
            recommendations.append(f"建议重点关注{weak_area}方面的提升")
        
        if metrics["response_time"] > 90:
            recommendations.append("建议通过更多练习提高反应速度")
        
        return recommendations[:4] if recommendations else ["继续保持良好的学习表现"]
    
    async def _generate_behavior_recommendations(self, metrics: Dict[str, Any], user_id: str) -> List[str]:
        """生成行为改进建议"""
        
        recommendations = []
        
        if metrics["session_frequency"] < 3:
            recommendations.append("建议增加学习频率，每周至少学习3-4次")
        
        if metrics["session_duration"] < 30:
            recommendations.append("建议延长单次学习时间，提高学习深度")
        
        if metrics["engagement_level"] < 0.7:
            recommendations.append("建议尝试更多样化的学习方式，提高学习兴趣")
        
        if metrics["self_regulation"] < 0.6:
            recommendations.append("建议培养自我监控和调节能力，制定学习策略")
        
        return recommendations[:4] if recommendations else ["继续保持良好的学习习惯"]
    
    def _parse_insights_list(self, text: str) -> List[str]:
        """解析洞察列表"""
        insights = []
        for line in text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                # 清理格式符号
                insight = line.lstrip('- •*1234567890. ').strip()
                if insight:
                    insights.append(insight)
        return insights
    
    def _analyze_progress_trends(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析进度趋势"""
        return {
            "trend_direction": "上升" if progress_data["weekly_completion"] > 0.15 else "稳定",
            "learning_acceleration": progress_data["topics_per_week"] > 5,
            "consistency_trend": "稳定" if progress_data["consistency"] > 0.7 else "波动"
        }
    
    def _compare_with_peers(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """与同伴比较"""
        # 模拟同伴平均数据
        peer_avg = {
            "completion_rate": 0.65,
            "topics_per_week": 4.5,
            "total_hours": 45
        }
        
        return {
            "completion_vs_peers": "高于平均" if progress_data["completion_rate"] > peer_avg["completion_rate"] else "低于平均",
            "speed_vs_peers": "快于平均" if progress_data["topics_per_week"] > peer_avg["topics_per_week"] else "慢于平均",
            "effort_vs_peers": "高于平均" if progress_data["total_hours"] > peer_avg["total_hours"] else "低于平均"
        }
    
    def _analyze_skill_mastery(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析技能掌握情况"""
        return {
            "mastered_skills": performance_data["strengths"],
            "developing_skills": performance_data["weaknesses"],
            "mastery_level": "高级" if performance_data["avg_score"] > 85 else "中级" if performance_data["avg_score"] > 70 else "初级"
        }
    
    def _calculate_learning_efficiency(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算学习效率"""
        return {
            "efficiency_score": round(performance_data["avg_score"] / 100 * performance_data["accuracy"], 2),
            "time_efficiency": "高效" if performance_data["avg_response_time"] < 60 else "一般",
            "improvement_efficiency": "快速" if performance_data["improvement"] > 0.15 else "稳步"
        }
    
    def _identify_learning_patterns(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """识别学习模式"""
        return {
            "learning_style": "规律型" if behavior_data["sessions_per_week"] >= 4 else "灵活型",
            "session_preference": "长时间" if behavior_data["avg_session_duration"] > 45 else "短时间",
            "peak_performance_time": behavior_data["peak_hours"][0] if behavior_data["peak_hours"] else "未知"
        }
    
    def _identify_optimization_opportunities(self, behavior_data: Dict[str, Any]) -> List[str]:
        """识别优化机会"""
        opportunities = []
        
        if behavior_data["avg_session_duration"] < 30:
            opportunities.append("延长学习时间以提高深度")
        
        if behavior_data["engagement_score"] < 0.7:
            opportunities.append("增加互动性学习活动")
        
        if behavior_data["self_regulation_score"] < 0.6:
            opportunities.append("加强学习策略指导")
        
        return opportunities

# 全局服务实例
analytics_service = AnalyticsService()

def get_analytics_service() -> AnalyticsService:
    """获取学习分析服务实例"""
    return analytics_service