# 个性化学习引擎服务
# Personalization Learning Engine Service

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.schemas import (
    LearningContext, LearningStyleData, CognitiveState,
    PersonalizedContentRequest, PersonalizedContentResponse,
    LearningPathRequest, LearningPathResponse
)
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.agent_manager import get_agent_manager

settings = get_settings()
logger = get_logger("app.personalization")

class PersonalizationService:
    """个性化学习引擎服务"""
    
    def __init__(self):
        self.agent_manager = get_agent_manager()
    
    async def generate_personalized_content(
        self, 
        request: PersonalizedContentRequest
    ) -> PersonalizedContentResponse:
        """生成个性化学习内容"""
        try:
            logger.info(f"生成个性化内容: {request.topic} - {request.content_type}")
            
            # 分析学习风格偏好
            style_analysis = self._analyze_learning_style(request.context.learning_style)
            
            # 根据认知状态调整内容难度
            difficulty_adjustment = self._calculate_difficulty_adjustment(
                request.context.cognitive_state
            )
            
            # 构建个性化提示词
            personalized_prompt = self._build_personalized_prompt(
                request.topic,
                request.content_type,
                style_analysis,
                difficulty_adjustment,
                request.context
            )
            
            # 选择合适的智能体
            agent_type = self._select_agent_for_content_type(request.content_type)
            
            # 生成内容
            content = await self.agent_manager.chat_with_agent(
                agent_type=agent_type,
                message=personalized_prompt,
                context=request.context.dict()
            )
            
            # 计算学习风格匹配度
            style_match = self._calculate_style_match(
                request.context.learning_style,
                request.content_type
            )
            
            return PersonalizedContentResponse(
                success=True,
                message="个性化内容生成成功",
                data={
                    "content": content,
                    "content_type": request.content_type,
                    "difficulty_level": min(5, max(1, int(request.context.difficulty_level + difficulty_adjustment))),
                    "learning_style_match": style_match
                },
                content=content,
                content_type=request.content_type,
                difficulty_level=min(5, max(1, int(request.context.difficulty_level + difficulty_adjustment))),
                learning_style_match=style_match
            )
            
        except Exception as e:
            logger.error(f"个性化内容生成失败: {e}")
            return PersonalizedContentResponse(
                success=False,
                message=f"个性化内容生成失败: {str(e)}",
                content="",
                content_type=request.content_type,
                difficulty_level=request.context.difficulty_level,
                learning_style_match={}
            )
    
    async def generate_learning_path(
        self, 
        request: LearningPathRequest
    ) -> LearningPathResponse:
        """生成个性化学习路径"""
        try:
            logger.info(f"生成学习路径: {request.subject} - {request.target_skills}")
            
            # 分析学习者特征
            learner_profile = self._build_learner_profile(request.context)
            
            # 构建路径生成提示词
            path_prompt = self._build_path_generation_prompt(
                request.subject,
                request.target_skills,
                learner_profile
            )
            
            # 使用专家智能体生成学习路径
            path_content = await self.agent_manager.chat_with_agent(
                agent_type="expert",
                message=path_prompt,
                context=request.context.dict()
            )
            
            # 解析和结构化路径数据
            structured_path = self._structure_learning_path(
                path_content,
                request.target_skills,
                request.context
            )
            
            path_id = str(uuid.uuid4())
            
            return LearningPathResponse(
                success=True,
                message="学习路径生成成功",
                data=structured_path,
                path_id=path_id,
                steps=structured_path["steps"],
                estimated_duration=structured_path["estimated_duration"],
                difficulty_progression=structured_path["difficulty_progression"]
            )
            
        except Exception as e:
            logger.error(f"学习路径生成失败: {e}")
            return LearningPathResponse(
                success=False,
                message=f"学习路径生成失败: {str(e)}",
                path_id="",
                steps=[],
                estimated_duration=0,
                difficulty_progression=[]
            )
    
    def _analyze_learning_style(self, learning_style: LearningStyleData) -> Dict[str, Any]:
        """分析学习风格偏好"""
        styles = {
            "visual": learning_style.visual,
            "auditory": learning_style.auditory,
            "reading": learning_style.reading,
            "kinesthetic": learning_style.kinesthetic
        }
        
        # 找出主导学习风格
        dominant_style = max(styles, key=styles.get)
        
        return {
            "dominant_style": dominant_style,
            "style_scores": styles,
            "is_multimodal": len([s for s in styles.values() if s > 0.6]) > 1
        }
    
    def _calculate_difficulty_adjustment(self, cognitive_state: CognitiveState) -> float:
        """根据认知状态计算难度调整"""
        # 认知负荷过高时降低难度
        if cognitive_state.cognitive_load > settings.cognitive_load_threshold:
            return -1.0
        
        # 理解率高且注意力集中时可以提高难度
        if (cognitive_state.comprehension_rate > 0.8 and 
            cognitive_state.attention_level > 0.7):
            return 0.5
        
        return 0.0
    
    def _build_personalized_prompt(
        self,
        topic: str,
        content_type: str,
        style_analysis: Dict[str, Any],
        difficulty_adjustment: float,
        context: LearningContext
    ) -> str:
        """构建个性化提示词"""
        
        style_guidance = {
            "visual": "使用图表、图像描述、视觉化比喻和结构化布局",
            "auditory": "使用对话形式、音韵记忆法、口语化表达",
            "reading": "提供详细文字说明、列表、定义和书面材料",
            "kinesthetic": "包含实践活动、动手操作、真实案例和体验式学习"
        }
        
        content_instructions = {
            "explanation": "提供清晰的概念解释和原理说明",
            "exercise": "设计适合的练习题和实践活动",
            "example": "给出具体的例子和应用场景"
        }
        
        prompt = f"""
请为学习主题「{topic}」生成{content_instructions.get(content_type, '相关内容')}。

学习者特征：
- 主导学习风格：{style_analysis['dominant_style']}
- 当前难度等级：{context.difficulty_level}
- 学习进度：{context.cognitive_state.learning_progress:.1%}
- 理解率：{context.cognitive_state.comprehension_rate:.1%}

内容要求：
1. {style_guidance.get(style_analysis['dominant_style'], '采用多样化的表达方式')}
2. 难度调整：{'降低难度，简化表达' if difficulty_adjustment < 0 else '适当提高挑战性' if difficulty_adjustment > 0 else '保持当前难度'}
3. 结合学习历史：{', '.join(context.learning_history[-3:]) if context.learning_history else '无'}
4. 内容应该实用、准确、易于理解

请生成个性化的学习内容。
"""
        
        return prompt
    
    def _select_agent_for_content_type(self, content_type: str) -> str:
        """根据内容类型选择合适的智能体"""
        agent_mapping = {
            "explanation": "expert",    # 专家智能体适合概念解释
            "exercise": "assistant",   # 助教智能体适合练习指导
            "example": "peer"          # 同伴智能体适合举例说明
        }
        
        return agent_mapping.get(content_type, "assistant")
    
    def _calculate_style_match(
        self, 
        learning_style: LearningStyleData, 
        content_type: str
    ) -> Dict[str, float]:
        """计算学习风格匹配度"""
        
        # 不同内容类型对学习风格的适配度
        type_style_affinity = {
            "explanation": {
                "visual": 0.8, "auditory": 0.6, "reading": 0.9, "kinesthetic": 0.4
            },
            "exercise": {
                "visual": 0.6, "auditory": 0.5, "reading": 0.7, "kinesthetic": 0.9
            },
            "example": {
                "visual": 0.9, "auditory": 0.7, "reading": 0.6, "kinesthetic": 0.8
            }
        }
        
        affinity = type_style_affinity.get(content_type, {
            "visual": 0.7, "auditory": 0.7, "reading": 0.7, "kinesthetic": 0.7
        })
        
        return {
            "visual": learning_style.visual * affinity["visual"],
            "auditory": learning_style.auditory * affinity["auditory"],
            "reading": learning_style.reading * affinity["reading"],
            "kinesthetic": learning_style.kinesthetic * affinity["kinesthetic"]
        }
    
    def _build_learner_profile(self, context: LearningContext) -> Dict[str, Any]:
        """构建学习者画像"""
        return {
            "learning_style": context.learning_style.dict(),
            "cognitive_state": context.cognitive_state.dict(),
            "current_level": context.difficulty_level,
            "learning_history": context.learning_history,
            "current_topic": context.current_topic
        }
    
    def _build_path_generation_prompt(
        self,
        subject: str,
        target_skills: List[str],
        learner_profile: Dict[str, Any]
    ) -> str:
        """构建路径生成提示词"""
        
        prompt = f"""
请为学科「{subject}」设计一个个性化学习路径，帮助学习者掌握以下技能：
{chr(10).join([f'- {skill}' for skill in target_skills])}

学习者画像：
- 主导学习风格：{max(learner_profile['learning_style'], key=learner_profile['learning_style'].get)}
- 当前认知负荷：{learner_profile['cognitive_state']['cognitive_load']:.1%}
- 理解率：{learner_profile['cognitive_state']['comprehension_rate']:.1%}
- 当前难度等级：{learner_profile['current_level']}

请设计包含以下要素的学习路径：
1. 学习步骤（每步包含目标、内容、活动、评估）
2. 预估学习时长
3. 难度递进安排
4. 个性化建议

请以结构化的方式回复。
"""
        
        return prompt
    
    def _structure_learning_path(
        self,
        path_content: str,
        target_skills: List[str],
        context: LearningContext
    ) -> Dict[str, Any]:
        """结构化学习路径数据"""
        
        # 这里应该解析AI生成的路径内容
        # 为了简化，我们创建一个基础结构
        
        num_steps = len(target_skills)
        base_duration = 30  # 每个技能基础学习时间30分钟
        
        steps = []
        difficulty_progression = []
        
        for i, skill in enumerate(target_skills):
            step_difficulty = min(5, context.difficulty_level + i)
            
            steps.append({
                "step_id": i + 1,
                "title": f"掌握{skill}",
                "description": f"学习和练习{skill}相关知识和技能",
                "learning_objectives": [f"理解{skill}的核心概念", f"能够应用{skill}解决问题"],
                "activities": ["概念学习", "实践练习", "自我评估"],
                "estimated_duration": base_duration,
                "difficulty_level": step_difficulty,
                "prerequisites": target_skills[:i] if i > 0 else []
            })
            
            difficulty_progression.append(step_difficulty)
        
        return {
            "steps": steps,
            "estimated_duration": num_steps * base_duration,
            "difficulty_progression": difficulty_progression,
            "total_skills": len(target_skills),
            "personalization_notes": path_content[:200] + "..." if len(path_content) > 200 else path_content
        }

# 全局服务实例
personalization_service = PersonalizationService()

def get_personalization_service() -> PersonalizationService:
    """获取个性化学习引擎服务实例"""
    return personalization_service