# Database models for Legal Statute Analysis System

from .user import User
from .document import Document
from .legal_article import LegalArticle
from .question_analysis import QuestionAnalysis

__all__ = ["User", "Document", "LegalArticle", "QuestionAnalysis"]