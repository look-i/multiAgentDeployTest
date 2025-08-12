# 深度学习模式服务
# Deep Learning Mode Service

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.models.schemas import (
    LearningContext, DeepLearningRequest, DeepLearningResponse
)
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.agent_manager import get_agent_manager

settings = get_settings()
logger = get_logger("app.deep_learning")

class DeepLearningService:
    """深度学习模式服务"""
    
    def __init__(self):
        self.agent_manager = get_agent_manager()
    
    async def create_deep_learning_plan(
        self, 
        request: DeepLearningRequest
    ) -> DeepLearningResponse:
        """创建深度学习计划"""
        try:
            logger.info(f"创建深度学习计划: {request.topic} - {request.learning_goal}")
            
            # 分析学习目标复杂度
            goal_complexity = self._analyze_goal_complexity(request.learning_goal)
            
            # 构建深度学习提示词
            deep_learning_prompt = self._build_deep_learning_prompt(
                request.topic,
                request.learning_goal,
                goal_complexity,
                request.context
            )
            
            # 使用专家智能体生成深度学习计划
            plan_content = await self.agent_manager.chat_with_agent(
                agent_type="expert",
                message=deep_learning_prompt,
                context=request.context.dict()
            )
            
            # 生成核心概念
            key_concepts = await self._extract_key_concepts(
                request.topic, 
                request.learning_goal,
                request.context
            )
            
            # 生成练习题
            practice_exercises = await self._generate_practice_exercises(
                request.topic,
                key_concepts,
                request.context
            )
            
            # 构建评估标准
            assessment_criteria = self._build_assessment_criteria(
                request.learning_goal,
                key_concepts,
                goal_complexity
            )
            
            # 结构化学习计划
            structured_plan = self._structure_learning_plan(
                plan_content,
                request.topic,
                request.learning_goal,
                request.context
            )
            
            return DeepLearningResponse(
                success=True,
                message="深度学习计划创建成功",
                data={
                    "learning_plan": structured_plan,
                    "key_concepts": key_concepts,
                    "practice_exercises": practice_exercises,
                    "assessment_criteria": assessment_criteria
                },
                learning_plan=structured_plan,
                key_concepts=key_concepts,
                practice_exercises=practice_exercises,
                assessment_criteria=assessment_criteria
            )
            
        except Exception as e:
            logger.error(f"深度学习计划创建失败: {e}")
            return DeepLearningResponse(
                success=False,
                message=f"深度学习计划创建失败: {str(e)}",
                learning_plan={},
                key_concepts=[],
                practice_exercises=[],
                assessment_criteria=[]
            )
    
    def _analyze_goal_complexity(self, learning_goal: str) -> Dict[str, Any]:
        """分析学习目标复杂度"""
        
        # 复杂度指标
        complexity_indicators = {
            "cognitive_levels": {
                "remember": ["记住", "回忆", "识别", "列举"],
                "understand": ["理解", "解释", "概括", "比较"],
                "apply": ["应用", "使用", "实施", "解决"],
                "analyze": ["分析", "分解", "区分", "组织"],
                "evaluate": ["评估", "判断", "批评", "检验"],
                "create": ["创造", "设计", "构建", "规划"]
            }
        }
        
        # 检测认知层次
        detected_level = "understand"  # 默认理解层次
        max_complexity = 0
        
        for level, keywords in complexity_indicators["cognitive_levels"].items():
            for keyword in keywords:
                if keyword in learning_goal:
                    level_complexity = list(complexity_indicators["cognitive_levels"].keys()).index(level)
                    if level_complexity > max_complexity:
                        max_complexity = level_complexity
                        detected_level = level
        
        # 估算学习时长（小时）
        time_estimates = {
            "remember": 2,
            "understand": 4,
            "apply": 6,
            "analyze": 8,
            "evaluate": 10,
            "create": 12
        }
        
        return {
            "cognitive_level": detected_level,
            "complexity_score": max_complexity + 1,
            "estimated_hours": time_estimates.get(detected_level, 4),
            "requires_scaffolding": max_complexity >= 3
        }
    
    def _build_deep_learning_prompt(
        self,
        topic: str,
        learning_goal: str,
        goal_complexity: Dict[str, Any],
        context: LearningContext
    ) -> str:
        """构建深度学习提示词"""
        
        prompt = f"""
请为主题「{topic}」设计一个深度学习计划，学习目标是：{learning_goal}

学习者信息：
- 当前难度等级：{context.difficulty_level}
- 学习进度：{context.cognitive_state.learning_progress:.1%}
- 认知负荷：{context.cognitive_state.cognitive_load:.1%}
- 理解率：{context.cognitive_state.comprehension_rate:.1%}
- 主导学习风格：{max(context.learning_style.dict(), key=context.learning_style.dict().get)}

目标复杂度分析：
- 认知层次：{goal_complexity['cognitive_level']}
- 复杂度评分：{goal_complexity['complexity_score']}/6
- 预估学习时长：{goal_complexity['estimated_hours']}小时
- 需要脚手架支持：{'是' if goal_complexity['requires_scaffolding'] else '否'}

请设计包含以下要素的深度学习计划：

1. **学习阶段划分**（至少3个阶段）
   - 每个阶段的目标和重点
   - 阶段间的逻辑关系
   - 预估时间分配

2. **深度学习策略**
   - 概念建构方法
   - 知识迁移技巧
   - 元认知策略

3. **个性化适配**
   - 基于学习风格的活动设计
   - 认知负荷管理
   - 难度递进安排

4. **实践应用**
   - 真实情境应用
   - 问题解决练习
   - 创新思维训练

请提供详细、实用的深度学习计划。
"""
        
        return prompt
    
    async def _extract_key_concepts(
        self,
        topic: str,
        learning_goal: str,
        context: LearningContext
    ) -> List[str]:
        """提取核心概念"""
        
        concept_prompt = f"""
请识别学习主题「{topic}」中与目标「{learning_goal}」相关的核心概念。

要求：
1. 列出5-8个最重要的核心概念
2. 概念应该是基础性、关键性的
3. 概念之间应该有逻辑关联
4. 适合当前学习者的认知水平

请以简洁的列表形式回复，每行一个概念。
"""
        
        try:
            concepts_text = await self.agent_manager.chat_with_agent(
                agent_type="expert",
                message=concept_prompt,
                context=context.dict()
            )
            
            # 解析概念列表
            concepts = []
            for line in concepts_text.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and len(line) > 2:
                    # 清理格式符号
                    concept = line.lstrip('- •*1234567890. ').strip()
                    if concept:
                        concepts.append(concept)
            
            return concepts[:8]  # 最多返回8个概念
            
        except Exception as e:
            logger.error(f"核心概念提取失败: {e}")
            return ["基础概念", "核心原理", "应用方法", "实践技巧"]
    
    async def _generate_practice_exercises(
        self,
        topic: str,
        key_concepts: List[str],
        context: LearningContext
    ) -> List[Dict[str, Any]]:
        """生成练习题"""
        
        exercise_prompt = f"""
请为主题「{topic}」设计练习题，重点考查以下核心概念：
{chr(10).join([f'- {concept}' for concept in key_concepts])}

学习者特征：
- 难度等级：{context.difficulty_level}
- 主导学习风格：{max(context.learning_style.dict(), key=context.learning_style.dict().get)}

请设计3-5道不同类型的练习题：
1. 概念理解题
2. 应用分析题
3. 综合实践题

每道题请包含：
- 题目描述
- 题目类型
- 难度等级
- 预估完成时间
- 评分要点

请以结构化格式回复。
"""
        
        try:
            exercises_text = await self.agent_manager.chat_with_agent(
                agent_type="assistant",
                message=exercise_prompt,
                context=context.dict()
            )
            
            # 解析练习题（简化处理）
            exercises = []
            
            # 基于概念生成基础练习结构
            exercise_types = ["概念理解", "应用分析", "综合实践"]
            
            for i, concept in enumerate(key_concepts[:3]):
                exercise_type = exercise_types[i % len(exercise_types)]
                
                exercises.append({
                    "id": i + 1,
                    "title": f"{concept}相关{exercise_type}题",
                    "type": exercise_type,
                    "description": f"针对{concept}的{exercise_type}练习",
                    "difficulty_level": min(5, context.difficulty_level + i // 2),
                    "estimated_time": 15 + i * 10,  # 15-45分钟
                    "scoring_points": [
                        f"准确理解{concept}",
                        "逻辑清晰",
                        "应用恰当"
                    ],
                    "ai_generated_content": exercises_text[:100] + "..."
                })
            
            return exercises
            
        except Exception as e:
            logger.error(f"练习题生成失败: {e}")
            return [{
                "id": 1,
                "title": "基础练习",
                "type": "概念理解",
                "description": "基础概念理解练习",
                "difficulty_level": context.difficulty_level,
                "estimated_time": 20,
                "scoring_points": ["概念准确", "表达清晰"]
            }]
    
    def _build_assessment_criteria(
        self,
        learning_goal: str,
        key_concepts: List[str],
        goal_complexity: Dict[str, Any]
    ) -> List[str]:
        """构建评估标准"""
        
        base_criteria = [
            "概念理解的准确性和深度",
            "知识应用的恰当性和灵活性",
            "思维过程的逻辑性和条理性",
            "表达的清晰性和完整性"
        ]
        
        # 根据认知层次添加特定标准
        cognitive_criteria = {
            "remember": ["信息回忆的准确性", "关键要点的完整性"],
            "understand": ["概念解释的清晰度", "举例说明的恰当性"],
            "apply": ["方法应用的正确性", "问题解决的有效性"],
            "analyze": ["分析过程的系统性", "要素识别的全面性"],
            "evaluate": ["判断标准的合理性", "评价结论的客观性"],
            "create": ["创新思维的独特性", "方案设计的可行性"]
        }
        
        specific_criteria = cognitive_criteria.get(
            goal_complexity["cognitive_level"], 
            ["学习成果的质量"]
        )
        
        # 基于核心概念添加评估点
        concept_criteria = [f"{concept}掌握程度" for concept in key_concepts[:3]]
        
        return base_criteria + specific_criteria + concept_criteria
    
    def _structure_learning_plan(
        self,
        plan_content: str,
        topic: str,
        learning_goal: str,
        context: LearningContext
    ) -> Dict[str, Any]:
        """结构化学习计划"""
        
        # 基础学习阶段
        phases = [
            {
                "phase_id": 1,
                "title": "基础建构阶段",
                "description": "建立核心概念理解，奠定学习基础",
                "duration_hours": 2,
                "activities": [
                    "概念学习与理解",
                    "基础知识梳理",
                    "初步应用练习"
                ],
                "learning_strategies": [
                    "概念图构建",
                    "类比学习",
                    "反思总结"
                ]
            },
            {
                "phase_id": 2,
                "title": "深化理解阶段",
                "description": "深入理解概念内涵，建立知识联系",
                "duration_hours": 3,
                "activities": [
                    "深度分析与探究",
                    "知识关联建构",
                    "案例分析练习"
                ],
                "learning_strategies": [
                    "问题导向学习",
                    "协作探究",
                    "批判性思维"
                ]
            },
            {
                "phase_id": 3,
                "title": "应用实践阶段",
                "description": "将知识应用于实际情境，提升实践能力",
                "duration_hours": 3,
                "activities": [
                    "实际问题解决",
                    "创新应用设计",
                    "成果展示交流"
                ],
                "learning_strategies": [
                    "项目式学习",
                    "设计思维",
                    "同伴评议"
                ]
            }
        ]
        
        return {
            "topic": topic,
            "learning_goal": learning_goal,
            "total_duration_hours": sum(phase["duration_hours"] for phase in phases),
            "phases": phases,
            "personalization_notes": {
                "learning_style_adaptations": self._get_style_adaptations(context.learning_style),
                "cognitive_load_management": self._get_cognitive_strategies(context.cognitive_state),
                "difficulty_progression": "渐进式难度提升，确保学习者能够跟上节奏"
            },
            "success_indicators": [
                "能够准确解释核心概念",
                "能够在新情境中应用知识",
                "能够进行独立思考和分析",
                "能够创造性地解决问题"
            ],
            "ai_generated_details": plan_content[:300] + "..." if len(plan_content) > 300 else plan_content
        }
    
    def _get_style_adaptations(self, learning_style) -> List[str]:
        """获取学习风格适配建议"""
        styles = learning_style.dict()
        dominant_style = max(styles, key=styles.get)
        
        adaptations = {
            "visual": ["使用图表和视觉化工具", "提供结构化的学习材料", "鼓励制作思维导图"],
            "auditory": ["增加讨论和口头表达机会", "使用音频学习资源", "鼓励自我解释"],
            "reading": ["提供详细的文字材料", "鼓励笔记整理", "安排阅读和写作活动"],
            "kinesthetic": ["设计动手实践活动", "提供真实情境体验", "鼓励边做边学"]
        }
        
        return adaptations.get(dominant_style, ["采用多样化学习方式"])
    
    def _get_cognitive_strategies(self, cognitive_state) -> List[str]:
        """获取认知策略建议"""
        strategies = []
        
        if cognitive_state.cognitive_load > 0.7:
            strategies.extend([
                "分解复杂任务为小步骤",
                "提供更多的脚手架支持",
                "增加休息和反思时间"
            ])
        
        if cognitive_state.attention_level < 0.6:
            strategies.extend([
                "使用多样化的学习活动",
                "设置明确的学习目标",
                "提供及时的反馈"
            ])
        
        if cognitive_state.comprehension_rate < 0.7:
            strategies.extend([
                "提供更多的解释和示例",
                "鼓励主动提问",
                "安排同伴互助学习"
            ])
        
        return strategies if strategies else ["保持当前学习节奏"]

# 全局服务实例
deep_learning_service = DeepLearningService()

def get_deep_learning_service() -> DeepLearningService:
    """获取深度学习模式服务实例"""
    return deep_learning_service