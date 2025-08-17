"""
Legal Article model for storing and indexing legal statutes
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property

from ..core.database import Base


class LegalArticle(Base):
    """Legal Article model for storing legal statutes and regulations"""
    
    __tablename__ = "legal_articles"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Article identification
    law_name = Column(String(255), nullable=False, index=True)  # 法規名稱
    article_number = Column(String(50), nullable=False, index=True)  # 條文編號
    article_title = Column(String(500), nullable=True)  # 條文標題
    
    # Content
    article_content = Column(Text, nullable=False)  # 條文內容
    article_summary = Column(Text, nullable=True)  # 條文摘要
    
    # Classification
    law_category = Column(String(100), nullable=False, index=True)  # 法規類別
    subject_tags = Column(JSON, nullable=True)  # 主題標籤
    
    # Hierarchy
    chapter = Column(String(100), nullable=True)  # 章
    section = Column(String(100), nullable=True)  # 節
    subsection = Column(String(100), nullable=True)  # 款
    
    # Legal metadata
    effective_date = Column(DateTime, nullable=True)  # 生效日期
    amendment_date = Column(DateTime, nullable=True)  # 修正日期
    legal_source = Column(String(255), nullable=True)  # 法源
    
    # Search and analysis
    keywords = Column(JSON, nullable=True)  # 關鍵字
    related_articles = Column(JSON, nullable=True)  # 相關條文ID
    
    # Vector embeddings for semantic search (PostgreSQL with pgvector)
    # Will be enabled when pgvector extension is available
    # from sqlalchemy.dialects.postgresql import ARRAY
    # from pgvector.sqlalchemy import Vector
    # embedding_vector = Column(Vector(1536), nullable=True)  # OpenAI embedding dimension
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LegalArticle(id={self.id}, law={self.law_name}, article={self.article_number})>"
    
    def to_dict(self):
        """Convert legal article to dictionary"""
        return {
            "id": str(self.id),
            "law_name": self.law_name,
            "article_number": self.article_number,
            "article_title": self.article_title,
            "article_content": self.article_content,
            "article_summary": self.article_summary,
            "law_category": self.law_category,
            "subject_tags": self.subject_tags,
            "chapter": self.chapter,
            "section": self.section,
            "subsection": self.subsection,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "amendment_date": self.amendment_date.isoformat() if self.amendment_date else None,
            "legal_source": self.legal_source,
            "keywords": self.keywords,
            "related_articles": self.related_articles,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @hybrid_property
    def full_citation(self) -> str:
        """Get full legal citation"""
        return f"{self.law_name} 第 {self.article_number} 條"
    
    @property
    def has_summary(self) -> bool:
        """Check if article has summary"""
        return self.article_summary is not None and len(self.article_summary.strip()) > 0