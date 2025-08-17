"""
Legal Question Analysis API endpoints
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..core.database import get_db
from .auth import get_current_user
from ..services.analysis_service import analysis_service
from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])


class QuestionAnalysisRequest(BaseModel):
    """Request model for question analysis"""
    question_text: str = Field(..., min_length=10, max_length=5000, description="Legal question to analyze")
    document_id: Optional[str] = Field(None, description="Document ID if question is from uploaded document")
    context: Optional[str] = Field(None, max_length=1000, description="Additional context about the question")
    question_type_hint: Optional[str] = Field(None, description="Hint about question type")


class AnalysisRatingRequest(BaseModel):
    """Request model for rating analysis"""
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating from 1-5")
    feedback: Optional[str] = Field(None, max_length=1000, description="Optional feedback")


@router.post("/question", status_code=status.HTTP_201_CREATED)
async def analyze_question(
    request: QuestionAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a legal question using AI
    
    This endpoint performs comprehensive analysis of legal questions including:
    - Question type classification
    - Difficulty assessment
    - Relevant law identification
    - Key concept extraction
    - Study recommendations
    """
    try:
        logger.info(f"Analyzing question for user {current_user.id}")
        
        # Perform analysis
        result = await analysis_service.analyze_question(
            question_text=request.question_text,
            user_id=str(current_user.id),
            db=db,
            document_id=request.document_id,
            context=request.context,
            question_type_hint=request.question_type_hint
        )
        
        return {
            "message": "Question analysis completed successfully",
            "analysis": result
        }
        
    except Exception as e:
        logger.error(f"Question analysis failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze question"
        )


@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analysis results by ID
    """
    analysis = analysis_service.get_analysis(
        analysis_id=analysis_id,
        user_id=str(current_user.id),
        db=db
    )
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return {
        "analysis": analysis.to_dict()
    }


@router.get("/")
async def list_analyses(
    limit: int = Query(20, ge=1, le=100, description="Number of analyses to return"),
    offset: int = Query(0, ge=0, description="Number of analyses to skip"),
    question_type: Optional[str] = Query(None, description="Filter by question type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's question analyses with pagination and filtering
    """
    analyses = analysis_service.get_user_analyses(
        user_id=str(current_user.id),
        db=db,
        limit=limit,
        offset=offset,
        question_type_filter=question_type
    )
    
    return {
        "analyses": [analysis.to_dict() for analysis in analyses],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": len(analyses)
        }
    }


@router.post("/{analysis_id}/rate")
async def rate_analysis(
    analysis_id: str,
    request: AnalysisRatingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rate an analysis result and provide feedback
    """
    success = await analysis_service.rate_analysis(
        analysis_id=analysis_id,
        user_id=str(current_user.id),
        rating=request.rating,
        feedback=request.feedback,
        db=db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found or could not be rated"
        )
    
    return {
        "message": "Analysis rated successfully",
        "analysis_id": analysis_id,
        "rating": request.rating
    }


@router.get("/stats/summary")
async def get_analysis_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analysis statistics for the current user
    """
    stats = analysis_service.get_analysis_stats(
        user_id=str(current_user.id),
        db=db
    )
    
    return {
        "user_id": str(current_user.id),
        "statistics": stats
    }


@router.get("/types/available")
async def get_question_types():
    """
    Get available question types for filtering
    """
    return {
        "question_types": [
            {"value": "選擇題", "label": "選擇題"},
            {"value": "問答題", "label": "問答題"},
            {"value": "申論題", "label": "申論題"},
            {"value": "案例分析", "label": "案例分析"},
            {"value": "未分類", "label": "未分類"}
        ],
        "difficulty_levels": [
            {"value": "初級", "label": "初級"},
            {"value": "中級", "label": "中級"},
            {"value": "高級", "label": "高級"},
            {"value": "專業", "label": "專業"}
        ]
    }