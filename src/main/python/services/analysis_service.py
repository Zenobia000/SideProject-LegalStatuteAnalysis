"""
Analysis service for legal question analysis and management
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.question_analysis import QuestionAnalysis
from ..models.document import Document
from ..models.legal_article import LegalArticle
from .llm_service import llm_service, LegalAnalysisResult
from .document_service import document_service
from ..core.config import settings

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for managing legal question analysis"""
    
    def __init__(self):
        self.llm_service = llm_service
    
    async def analyze_question(
        self,
        question_text: str,
        user_id: str,
        db: Session,
        document_id: Optional[str] = None,
        context: Optional[str] = None,
        question_type_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a legal question using AI
        
        Args:
            question_text: The question to analyze
            user_id: User ID requesting the analysis
            db: Database session
            document_id: Optional document ID if question is from a document
            context: Additional context
            question_type_hint: Hint about question type
            
        Returns:
            Analysis result dictionary
        """
        logger.info(f"Starting analysis for user {user_id}")
        
        try:
            # Check if LLM service is available
            if not self.llm_service.is_available():
                logger.warning("LLM service not available, using fallback analysis")
                return await self._fallback_analysis(
                    question_text, user_id, db, document_id
                )
            
            # Perform AI analysis
            analysis_result, metadata = await self.llm_service.analyze_legal_question(
                question_text=question_text,
                context=context,
                question_type_hint=question_type_hint
            )
            
            # Create database record
            question_analysis = QuestionAnalysis(
                user_id=user_id,
                document_id=document_id,
                question_text=question_text,
                question_type=analysis_result.question_type,
                question_difficulty=analysis_result.difficulty_level,
                confidence_score=analysis_result.confidence_score,
                study_suggestions=analysis_result.study_suggestions,
                ai_model_used=metadata.get("model_used"),
                processing_time_ms=metadata.get("processing_time_ms")
            )
            
            # Set analysis result as JSON
            question_analysis.set_analysis_result({
                "answer_approach": analysis_result.answer_approach,
                "key_points": analysis_result.key_points,
                "metadata": metadata
            })
            
            # Set relevant laws
            question_analysis.relevant_laws = analysis_result.relevant_laws
            
            # Set legal concepts
            legal_concepts_list = []
            for concept in analysis_result.legal_concepts:
                legal_concepts_list.append({
                    "concept": concept.get("concept", ""),
                    "description": concept.get("description", ""),
                    "importance": concept.get("importance", "中等")
                })
            question_analysis.legal_concepts = legal_concepts_list
            
            # Set key points
            question_analysis.key_points = analysis_result.key_points
            
            # Save to database
            db.add(question_analysis)
            db.commit()
            db.refresh(question_analysis)
            
            # Enhance with additional analysis
            await self._enhance_analysis(question_analysis, db)
            
            logger.info(f"Analysis completed for question ID: {question_analysis.id}")
            
            return {
                "analysis_id": str(question_analysis.id),
                "question_type": analysis_result.question_type,
                "difficulty_level": analysis_result.difficulty_level,
                "confidence_score": analysis_result.confidence_score,
                "relevant_laws": analysis_result.relevant_laws,
                "legal_concepts": legal_concepts_list,
                "key_points": analysis_result.key_points,
                "answer_approach": analysis_result.answer_approach,
                "study_suggestions": analysis_result.study_suggestions,
                "processing_metadata": metadata,
                "created_at": question_analysis.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Analysis failed for user {user_id}: {e}")
            # Rollback transaction
            db.rollback()
            
            # Return fallback analysis
            return await self._fallback_analysis(
                question_text, user_id, db, document_id
            )
    
    async def _fallback_analysis(
        self,
        question_text: str,
        user_id: str,
        db: Session,
        document_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fallback analysis when AI service is unavailable"""
        
        # Basic pattern matching for question types
        question_type = self._classify_question_basic(question_text)
        difficulty = self._estimate_difficulty_basic(question_text)
        
        # Create minimal analysis record
        question_analysis = QuestionAnalysis(
            user_id=user_id,
            document_id=document_id,
            question_text=question_text,
            question_type=question_type,
            question_difficulty=difficulty,
            confidence_score=0.3,  # Low confidence for fallback
            study_suggestions="請諮詢法律專家或使用完整AI分析功能",
            ai_model_used="fallback_classifier"
        )
        
        question_analysis.set_analysis_result({
            "method": "fallback",
            "note": "AI服務暫時不可用，使用基礎分類"
        })
        
        db.add(question_analysis)
        db.commit()
        db.refresh(question_analysis)
        
        return {
            "analysis_id": str(question_analysis.id),
            "question_type": question_type,
            "difficulty_level": difficulty,
            "confidence_score": 0.3,
            "relevant_laws": [],
            "legal_concepts": [],
            "key_points": ["需要完整AI分析功能"],
            "answer_approach": "請重試或使用手動分析",
            "study_suggestions": "請諮詢法律專家或使用完整AI分析功能",
            "processing_metadata": {"method": "fallback"},
            "created_at": question_analysis.created_at.isoformat()
        }
    
    def _classify_question_basic(self, question_text: str) -> str:
        """Basic question type classification using pattern matching"""
        text_lower = question_text.lower()
        
        if any(keyword in text_lower for keyword in ["選擇", "下列", "何者", "哪個"]):
            return "選擇題"
        elif any(keyword in text_lower for keyword in ["說明", "解釋", "論述", "分析"]):
            return "申論題"
        elif any(keyword in text_lower for keyword in ["案例", "事實", "情況", "甲乙"]):
            return "案例分析"
        elif "?" in question_text or "？" in question_text:
            return "問答題"
        else:
            return "未分類"
    
    def _estimate_difficulty_basic(self, question_text: str) -> str:
        """Basic difficulty estimation"""
        # Simple heuristics based on text length and complexity
        word_count = len(question_text)
        
        if word_count < 50:
            return "初級"
        elif word_count < 150:
            return "中級"
        else:
            return "高級"
    
    async def _enhance_analysis(self, question_analysis: QuestionAnalysis, db: Session):
        """Enhance analysis with additional data"""
        try:
            # Find similar questions in database
            similar_analyses = await self._find_similar_analyses(
                question_analysis, db
            )
            
            if similar_analyses:
                question_analysis.similar_questions = [
                    {
                        "id": str(analysis.id),
                        "question_text": analysis.question_text[:100] + "...",
                        "question_type": analysis.question_type,
                        "similarity_score": 0.7  # Placeholder
                    }
                    for analysis in similar_analyses[:3]
                ]
            
            # Find relevant legal articles
            relevant_articles = await self._find_relevant_articles(
                question_analysis.question_text, db
            )
            
            if relevant_articles:
                question_analysis.practice_materials = [
                    {
                        "title": article.title,
                        "law_name": article.law_name,
                        "article_number": article.article_number,
                        "relevance": "high"
                    }
                    for article in relevant_articles[:5]
                ]
            
            db.commit()
            
        except Exception as e:
            logger.warning(f"Failed to enhance analysis: {e}")
    
    async def _find_similar_analyses(
        self,
        target_analysis: QuestionAnalysis,
        db: Session,
        limit: int = 5
    ) -> List[QuestionAnalysis]:
        """Find similar question analyses"""
        try:
            # Simple similarity based on question type and concepts
            similar_analyses = db.query(QuestionAnalysis).filter(
                and_(
                    QuestionAnalysis.id != target_analysis.id,
                    QuestionAnalysis.question_type == target_analysis.question_type,
                    QuestionAnalysis.confidence_score > 0.5
                )
            ).limit(limit).all()
            
            return similar_analyses
            
        except Exception as e:
            logger.error(f"Error finding similar analyses: {e}")
            return []
    
    async def _find_relevant_articles(
        self,
        question_text: str,
        db: Session,
        limit: int = 5
    ) -> List[LegalArticle]:
        """Find relevant legal articles"""
        try:
            # Simple keyword matching for now
            # In production, this would use vector similarity
            keywords = self._extract_keywords(question_text)
            
            if not keywords:
                return []
            
            # Query legal articles containing keywords
            articles = []
            for keyword in keywords[:3]:  # Use top 3 keywords
                found_articles = db.query(LegalArticle).filter(
                    LegalArticle.content.ilike(f"%{keyword}%")
                ).limit(limit).all()
                articles.extend(found_articles)
            
            # Remove duplicates
            unique_articles = list({article.id: article for article in articles}.values())
            return unique_articles[:limit]
            
        except Exception as e:
            logger.error(f"Error finding relevant articles: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (simplified version)"""
        # Legal keywords commonly found in Taiwan law
        legal_keywords = [
            "契約", "財產", "損害", "責任", "權利", "義務", "法律", "條文",
            "民法", "刑法", "商業", "公司", "消費者", "保護", "管理", "條例"
        ]
        
        found_keywords = []
        for keyword in legal_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def get_analysis(
        self,
        analysis_id: str,
        user_id: str,
        db: Session
    ) -> Optional[QuestionAnalysis]:
        """Get analysis by ID"""
        try:
            analysis = db.query(QuestionAnalysis).filter(
                and_(
                    QuestionAnalysis.id == analysis_id,
                    QuestionAnalysis.user_id == user_id
                )
            ).first()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error retrieving analysis {analysis_id}: {e}")
            return None
    
    def get_user_analyses(
        self,
        user_id: str,
        db: Session,
        limit: int = 20,
        offset: int = 0,
        question_type_filter: Optional[str] = None
    ) -> List[QuestionAnalysis]:
        """Get user's question analyses with pagination"""
        try:
            query = db.query(QuestionAnalysis).filter(
                QuestionAnalysis.user_id == user_id
            )
            
            if question_type_filter:
                query = query.filter(
                    QuestionAnalysis.question_type == question_type_filter
                )
            
            analyses = query.order_by(
                QuestionAnalysis.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            return analyses
            
        except Exception as e:
            logger.error(f"Error retrieving user analyses: {e}")
            return []
    
    async def rate_analysis(
        self,
        analysis_id: str,
        user_id: str,
        rating: float,
        feedback: Optional[str],
        db: Session
    ) -> bool:
        """Rate an analysis result"""
        try:
            analysis = self.get_analysis(analysis_id, user_id, db)
            
            if not analysis:
                return False
            
            analysis.user_rating = rating
            analysis.user_feedback = feedback
            analysis.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Analysis {analysis_id} rated {rating}/5 by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error rating analysis {analysis_id}: {e}")
            db.rollback()
            return False
    
    def get_analysis_stats(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get analysis statistics for user"""
        try:
            total_analyses = db.query(QuestionAnalysis).filter(
                QuestionAnalysis.user_id == user_id
            ).count()
            
            # Group by question type
            type_stats = db.query(
                QuestionAnalysis.question_type,
                db.func.count(QuestionAnalysis.id).label('count')
            ).filter(
                QuestionAnalysis.user_id == user_id
            ).group_by(QuestionAnalysis.question_type).all()
            
            # Average confidence score
            avg_confidence = db.query(
                db.func.avg(QuestionAnalysis.confidence_score)
            ).filter(
                QuestionAnalysis.user_id == user_id
            ).scalar()
            
            # Recent activity (last 7 days)
            from datetime import timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_analyses = db.query(QuestionAnalysis).filter(
                and_(
                    QuestionAnalysis.user_id == user_id,
                    QuestionAnalysis.created_at >= week_ago
                )
            ).count()
            
            return {
                "total_analyses": total_analyses,
                "question_type_breakdown": {
                    row.question_type: row.count for row in type_stats
                },
                "average_confidence": float(avg_confidence) if avg_confidence else 0.0,
                "recent_activity": recent_analyses,
                "last_analysis": None  # Would add timestamp of last analysis
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis stats for user {user_id}: {e}")
            return {
                "total_analyses": 0,
                "question_type_breakdown": {},
                "average_confidence": 0.0,
                "recent_activity": 0
            }


# Global analysis service instance
analysis_service = AnalysisService()