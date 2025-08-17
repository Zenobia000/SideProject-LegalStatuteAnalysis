"""
Document upload and management API endpoints
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..core.database import get_db
from .auth import get_current_user
from ..services.document_service import document_service
from ..models.user import User
from ..models.document import Document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    process_immediately: bool = Query(True, description="Process document immediately after upload"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document for analysis
    
    - **file**: PDF or image file to upload
    - **process_immediately**: Whether to start OCR processing immediately
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file size
        contents = await file.read()
        file_size = len(contents)
        
        if not document_service.file_storage.check_file_size(file_size):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds limit: {file_size} bytes"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Upload and process document
        result = await document_service.upload_document(
            file=file.file,
            filename=file.filename,
            user_id=str(current_user.id),
            db=db,
            process_immediately=process_immediately
        )
        
        return {
            "message": "Document uploaded successfully",
            "document": result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get document details by ID
    """
    document = document_service.get_document(
        document_id=document_id,
        db=db,
        user_id=str(current_user.id)
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {
        "document": document.to_dict()
    }


@router.get("/{document_id}/content")
async def get_document_content(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get extracted text content from document
    """
    document = document_service.get_document(
        document_id=document_id,
        db=db,
        user_id=str(current_user.id)
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.processing_status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document processing not completed. Status: {document.processing_status}"
        )
    
    return {
        "document_id": str(document.id),
        "extracted_text": document.extracted_text,
        "page_count": document.page_count,
        "processing_metadata": document.ocr_metadata
    }


@router.post("/{document_id}/process")
async def process_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process document for text extraction (if not already processed)
    """
    # Check if document exists and belongs to user
    document = document_service.get_document(
        document_id=document_id,
        db=db,
        user_id=str(current_user.id)
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.processing_status == "completed":
        return {
            "message": "Document already processed",
            "document_id": document_id,
            "processing_status": "completed"
        }
    
    if document.processing_status == "processing":
        return {
            "message": "Document processing in progress",
            "document_id": document_id,
            "processing_status": "processing"
        }
    
    try:
        # Start processing
        result = await document_service.process_document(document_id, db)
        
        return {
            "message": "Document processing completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Document processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document"
        )


@router.get("/")
async def list_documents(
    limit: int = Query(20, ge=1, le=100, description="Number of documents to return"),
    offset: int = Query(0, ge=0, description="Number of documents to skip"),
    status: Optional[str] = Query(None, description="Filter by processing status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's documents with pagination and filtering
    """
    documents = document_service.get_user_documents(
        user_id=str(current_user.id),
        db=db,
        limit=limit,
        offset=offset,
        status_filter=status
    )
    
    return {
        "documents": [doc.to_dict() for doc in documents],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": len(documents)
        }
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document and its associated file
    """
    success = document_service.delete_document(
        document_id=document_id,
        db=db,
        user_id=str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or could not be deleted"
        )
    
    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }


@router.get("/stats/summary")
async def get_document_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get document statistics for the current user
    """
    stats = document_service.get_document_stats(
        user_id=str(current_user.id),
        db=db
    )
    
    return {
        "user_id": str(current_user.id),
        "statistics": stats
    }