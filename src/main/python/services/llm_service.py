"""
LLM (Large Language Model) service for AI-powered legal analysis
"""
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
import json

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from ..core.config import settings

logger = logging.getLogger(__name__)


class LegalAnalysisResult(BaseModel):
    """Structured output for legal analysis"""
    question_type: str = Field(description="題型分類 (選擇題/問答題/申論題/案例分析等)")
    difficulty_level: str = Field(description="難度等級 (初級/中級/高級/專業)")
    relevant_laws: List[Dict[str, Any]] = Field(description="相關法條列表")
    legal_concepts: List[Dict[str, str]] = Field(description="重要法律概念")
    key_points: List[str] = Field(description="解題要點")
    answer_approach: str = Field(description="解題思路和方法")
    study_suggestions: str = Field(description="學習建議")
    confidence_score: float = Field(description="分析信心分數 (0-1)", ge=0.0, le=1.0)


class LLMService:
    """LLM service for legal text analysis using OpenAI GPT"""
    
    def __init__(self):
        self.model_name = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self._llm = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize OpenAI ChatGPT model"""
        try:
            if not settings.openai_api_key:
                logger.warning("OpenAI API key not configured, LLM functionality will be limited")
                return
            
            self._llm = ChatOpenAI(
                model_name=self.model_name,
                openai_api_key=settings.openai_api_key,
                max_tokens=self.max_tokens,
                temperature=0.1,  # Low temperature for consistent legal analysis
                request_timeout=60
            )
            logger.info(f"LLM service initialized with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            self._llm = None
    
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        return self._llm is not None
    
    async def analyze_legal_question(
        self,
        question_text: str,
        context: Optional[str] = None,
        question_type_hint: Optional[str] = None
    ) -> Tuple[LegalAnalysisResult, Dict[str, Any]]:
        """
        Analyze a legal question using LLM
        
        Args:
            question_text: The legal question to analyze
            context: Additional context about the question
            question_type_hint: Hint about question type
            
        Returns:
            Tuple of (analysis_result, metadata)
        """
        if not self.is_available():
            raise RuntimeError("LLM service not available")
        
        start_time = time.time()
        
        try:
            # Prepare the analysis prompt
            system_prompt = self._get_system_prompt()
            user_prompt = self._format_question_prompt(
                question_text, context, question_type_hint
            )
            
            # Create parser for structured output
            parser = PydanticOutputParser(pydantic_object=LegalAnalysisResult)
            format_instructions = parser.get_format_instructions()
            
            # Add format instructions to the prompt
            user_prompt += f"\\n\\n{format_instructions}"
            
            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # Get LLM response
            response = await self._llm.agenerate([messages])
            response_text = response.generations[0][0].text
            
            # Parse structured output
            try:
                analysis_result = parser.parse(response_text)
            except Exception as parse_error:
                logger.warning(f"Failed to parse structured output: {parse_error}")
                # Fallback to basic parsing
                analysis_result = self._fallback_parse(response_text)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Prepare metadata
            metadata = {
                "model_used": self.model_name,
                "processing_time_ms": processing_time,
                "prompt_tokens": len(user_prompt.split()),
                "response_tokens": len(response_text.split()),
                "success": True
            }
            
            logger.info(f"Legal question analysis completed in {processing_time:.2f}ms")
            return analysis_result, metadata
            
        except Exception as e:
            error_time = (time.time() - start_time) * 1000
            logger.error(f"LLM analysis failed after {error_time:.2f}ms: {e}")
            
            # Return fallback result
            fallback_result = self._get_fallback_result(question_text)
            metadata = {
                "model_used": self.model_name,
                "processing_time_ms": error_time,
                "success": False,
                "error": str(e)
            }
            
            return fallback_result, metadata
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for legal analysis"""
        return """你是一位專業的法律專家，專門分析臺灣國家考試的法律題目。你的任務是：

1. 分析題型和難度等級
2. 識別相關的法條和法律概念
3. 提供解題要點和思路
4. 給出學習建議

請用繁體中文回答，並確保分析準確、實用。

重要規則：
- 專注於臺灣法律體系
- 提供具體的法條編號和條文
- 解釋必須清晰易懂
- 學習建議要具體可行
- 信心分數要客觀評估"""

    def _format_question_prompt(
        self, 
        question_text: str, 
        context: Optional[str] = None,
        question_type_hint: Optional[str] = None
    ) -> str:
        """Format the question analysis prompt"""
        prompt = f"請分析以下法律題目：\\n\\n【題目】\\n{question_text}\\n\\n"
        
        if context:
            prompt += f"【背景資訊】\\n{context}\\n\\n"
        
        if question_type_hint:
            prompt += f"【題型提示】\\n{question_type_hint}\\n\\n"
        
        prompt += """請提供完整的分析，包括：
1. 題型分類和難度評估
2. 相關法條和法律概念
3. 解題要點和關鍵思路
4. 學習建議和練習方向
5. 分析的信心程度

請以結構化的JSON格式回答。"""
        
        return prompt
    
    def _fallback_parse(self, response_text: str) -> LegalAnalysisResult:
        """Fallback parsing when structured parsing fails"""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
                return LegalAnalysisResult(**data)
        except Exception:
            pass
        
        # Ultimate fallback - create basic result
        return LegalAnalysisResult(
            question_type="未分類",
            difficulty_level="中級",
            relevant_laws=[],
            legal_concepts=[],
            key_points=["需要進一步分析"],
            answer_approach="LLM 分析失敗，建議手動分析",
            study_suggestions="請諮詢法律專家或查閱相關法條",
            confidence_score=0.1
        )
    
    def _get_fallback_result(self, question_text: str) -> LegalAnalysisResult:
        """Get fallback result when LLM fails"""
        return LegalAnalysisResult(
            question_type="待分析",
            difficulty_level="未知",
            relevant_laws=[],
            legal_concepts=[],
            key_points=["系統暫時無法分析此題目"],
            answer_approach="請重試或聯繫技術支援",
            study_suggestions="建議查閱相關法律教材或諮詢專業人士",
            confidence_score=0.0
        )
    
    async def extract_legal_concepts(self, text: str) -> List[Dict[str, str]]:
        """Extract legal concepts from text"""
        if not self.is_available():
            return []
        
        try:
            prompt = f"""從以下文本中提取重要的法律概念：

{text}

請以JSON格式返回概念列表，每個概念包含：
- concept: 概念名稱
- description: 簡要說明
- category: 法律領域分類

格式：[{{"concept": "...", "description": "...", "category": "..."}}]"""

            messages = [HumanMessage(content=prompt)]
            response = await self._llm.agenerate([messages])
            response_text = response.generations[0][0].text
            
            # Parse JSON response
            concepts = json.loads(response_text)
            return concepts
            
        except Exception as e:
            logger.error(f"Legal concept extraction failed: {e}")
            return []
    
    async def find_similar_questions(
        self, 
        question_text: str, 
        question_bank: List[str]
    ) -> List[Dict[str, Any]]:
        """Find similar questions from a question bank"""
        if not self.is_available():
            return []
        
        try:
            bank_text = "\\n".join([f"{i+1}. {q}" for i, q in enumerate(question_bank[:10])])
            
            prompt = f"""請找出與目標題目最相似的3-5道題目：

【目標題目】
{question_text}

【題庫】
{bank_text}

請以JSON格式返回相似題目，包含：
- question_number: 題號
- similarity_score: 相似度分數 (0-1)
- reason: 相似的原因

格式：[{{"question_number": 1, "similarity_score": 0.8, "reason": "..."}}]"""

            messages = [HumanMessage(content=prompt)]
            response = await self._llm.agenerate([messages])
            response_text = response.generations[0][0].text
            
            similar_questions = json.loads(response_text)
            return similar_questions
            
        except Exception as e:
            logger.error(f"Similar question search failed: {e}")
            return []


# Global LLM service instance
llm_service = LLMService()