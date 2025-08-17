"""
Question Analysis model for storing AI analysis results
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import json

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.database import Base


class QuestionAnalysis(Base):
    """Question Analysis model for storing AI analysis results of legal questions"""
    
    __tablename__ = "question_analyses"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True, index=True)
    
    # Question content
    question_text = Column(Text, nullable=False)  # 題目原文
    question_type = Column(String(50), nullable=True, index=True)  # 題型分類
    question_difficulty = Column(String(20), nullable=True)  # 難度等級
    
    # AI Analysis results
    analysis_result = Column(JSON, nullable=True)  # AI 分析結果 (JSON格式)
    confidence_score = Column(Float, nullable=True)  # 信心分數 (0-1)
    
    # Identified legal concepts
    relevant_laws = Column(JSON, nullable=True)  # 相關法條 (JSON array)
    legal_concepts = Column(JSON, nullable=True)  # 法律概念 (JSON array)
    key_points = Column(JSON, nullable=True)  # 重點分析 (JSON array)
    
    # Study recommendations
    study_suggestions = Column(Text, nullable=True)  # 學習建議
    similar_questions = Column(JSON, nullable=True)  # 類似題目 (JSON array)
    practice_materials = Column(JSON, nullable=True)  # 練習資料 (JSON array)
    
    # Processing metadata
    ai_model_used = Column(String(100), nullable=True)  # 使用的AI模型
    processing_time_ms = Column(Float, nullable=True)  # 處理時間(毫秒)
    
    # User interaction
    user_rating = Column(Float, nullable=True)  # 用戶評分 (1-5)
    user_feedback = Column(Text, nullable=True)  # 用戶回饋
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    document = relationship("Document", back_populates="analyses")
    
    def __repr__(self):
        return f"<QuestionAnalysis(id={self.id}, type={self.question_type}, confidence={self.confidence_score})>"
    
    def to_dict(self):
        """Convert question analysis to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "document_id": str(self.document_id) if self.document_id else None,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "question_difficulty": self.question_difficulty,
            "analysis_result": self.analysis_result,
            "confidence_score": self.confidence_score,
            "relevant_laws": self.relevant_laws,
            "legal_concepts": self.legal_concepts,
            "key_points": self.key_points,
            "study_suggestions": self.study_suggestions,
            "similar_questions": self.similar_questions,
            "practice_materials": self.practice_materials,
            "ai_model_used": self.ai_model_used,
            "processing_time_ms": self.processing_time_ms,
            "user_rating": self.user_rating,
            "user_feedback": self.user_feedback,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    def set_analysis_result(self, result: Dict[str, Any]):
        """Set analysis result as JSON"""
        self.analysis_result = result
    
    def get_analysis_result(self) -> Optional[Dict[str, Any]]:
        """Get analysis result from JSON"""
        return self.analysis_result
    
    def add_relevant_law(self, law_name: str, article_number: str, relevance_score: float):
        """Add a relevant law to the analysis"""
        if self.relevant_laws is None:
            self.relevant_laws = []
        
        self.relevant_laws.append({
            "law_name": law_name,
            "article_number": article_number,
            "relevance_score": relevance_score
        })
    
    def add_legal_concept(self, concept: str, description: str, importance: str):
        """Add a legal concept to the analysis"""
        if self.legal_concepts is None:
            self.legal_concepts = []
        
        self.legal_concepts.append({
            "concept": concept,
            "description": description,
            "importance": importance
        })
    
    @property
    def has_high_confidence(self) -> bool:
        """Check if analysis has high confidence (>0.8)"""
        return self.confidence_score is not None and self.confidence_score > 0.8
    
    @property
    def is_rated_by_user(self) -> bool:
        """Check if user has rated this analysis"""
        return self.user_rating is not None