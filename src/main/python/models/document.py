"""
Document model for PDF file management and OCR processing
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.database import Base


class Document(Base):
    """Document model for uploaded PDF files and OCR results"""
    
    __tablename__ = "documents"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # File metadata
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=False)
    
    # Processing status
    processing_status = Column(String(20), default="uploaded", nullable=False)
    # Status values: uploaded, processing, completed, failed
    
    # OCR results
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(String(10), nullable=True)  # Overall confidence score
    
    # Processing metadata
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    analyses = relationship("QuestionAnalysis", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, status={self.processing_status})>"
    
    def to_dict(self):
        """Convert document to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "filename": self.filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "processing_status": self.processing_status,
            "ocr_confidence": self.ocr_confidence,
            "processing_started_at": self.processing_started_at.isoformat() if self.processing_started_at else None,
            "processing_completed_at": self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @property
    def is_processing_complete(self) -> bool:
        """Check if document processing is complete"""
        return self.processing_status == "completed"
    
    @property
    def has_ocr_text(self) -> bool:
        """Check if document has OCR text available"""
        return self.ocr_text is not None and len(self.ocr_text.strip()) > 0