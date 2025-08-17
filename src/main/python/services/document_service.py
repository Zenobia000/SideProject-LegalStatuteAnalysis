"""
Document processing service for handling file uploads and text extraction
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.document import Document
from ..models.user import User
from ..utils.file_storage import file_storage
from ..utils.ocr import ocr_processor
from ..core.database import get_db

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for managing document uploads and processing"""
    
    def __init__(self):
        self.file_storage = file_storage
        self.ocr_processor = ocr_processor
        logger.info("Document service initialized")
    
    async def upload_document(
        self,
        file: BinaryIO,
        filename: str,
        user_id: str,
        db: Session,
        process_immediately: bool = True
    ) -> Dict[str, Any]:
        """
        Upload and process a document
        
        Args:
            file: Binary file object
            filename: Original filename
            user_id: ID of the uploading user
            db: Database session
            process_immediately: Whether to process OCR immediately
        
        Returns:
            Dict containing upload result and document info
        """
        try:
            # Validate file
            if not self.file_storage.is_allowed_file(filename):
                raise ValueError(f"File type not allowed: {Path(filename).suffix}")
            
            # Save file to storage
            unique_filename, file_path = self.file_storage.save_file(file, filename)
            
            # Get file info
            file_info = self.file_storage.get_file_info(unique_filename)
            if not file_info:
                raise RuntimeError("Failed to get file information")
            
            # Create database record
            document = Document(
                user_id=user_id,
                original_filename=filename,
                stored_filename=unique_filename,
                file_path=file_path,
                file_size=file_info["size"],
                mime_type=self._get_mime_type(filename),
                upload_status="uploaded",
                processing_status="pending"
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            logger.info(f"Document uploaded successfully: {document.id}")
            
            result = {
                "document_id": str(document.id),
                "original_filename": filename,
                "stored_filename": unique_filename,
                "file_size": file_info["size"],
                "upload_status": "success",
                "processing_status": "pending"
            }
            
            # Process document if requested
            if process_immediately:
                processing_result = await self.process_document(document.id, db)
                result.update(processing_result)
            
            return result
            
        except ValueError as e:
            logger.warning(f"Document upload validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Document upload error: {e}")
            # Clean up file if it was saved
            try:
                if 'unique_filename' in locals():
                    self.file_storage.delete_file(unique_filename)
            except Exception:
                pass
            raise RuntimeError(f"Failed to upload document: {str(e)}")
    
    async def process_document(self, document_id: str, db: Session) -> Dict[str, Any]:
        """
        Process uploaded document for text extraction
        
        Args:
            document_id: ID of the document to process
            db: Database session
        
        Returns:
            Dict containing processing results
        """
        try:
            # Get document record
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise ValueError(f"Document not found: {document_id}")
            
            # Update processing status
            document.processing_status = "processing"
            document.processing_started_at = datetime.utcnow()
            db.commit()
            
            # Get file path
            file_path = Path(document.file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Document file not found: {file_path}")
            
            # Extract text using OCR
            logger.info(f"Starting OCR processing for document: {document_id}")
            ocr_result = await self.ocr_processor.extract_text_async(file_path)
            
            # Update document with extracted content
            document.extracted_text = ocr_result.get("text", "")
            document.page_count = ocr_result["metadata"].get("total_pages", 1)
            document.ocr_metadata = ocr_result["metadata"]
            
            if ocr_result["metadata"].get("success", False):
                document.processing_status = "completed"
                logger.info(f"Document processing completed: {document_id}")
            else:
                document.processing_status = "failed"
                logger.warning(f"Document processing failed: {document_id}")
            
            document.processing_completed_at = datetime.utcnow()
            db.commit()
            
            return {
                "document_id": document_id,
                "processing_status": document.processing_status,
                "extracted_text": document.extracted_text,
                "page_count": document.page_count,
                "processing_metadata": document.ocr_metadata
            }
            
        except Exception as e:
            logger.error(f"Document processing error: {e}")
            
            # Update document status to failed
            try:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.processing_status = "failed"
                    document.processing_completed_at = datetime.utcnow()
                    document.error_message = str(e)
                    db.commit()
            except Exception:
                pass
            
            raise RuntimeError(f"Failed to process document: {str(e)}")
    
    def get_document(self, document_id: str, db: Session, user_id: Optional[str] = None) -> Optional[Document]:
        """
        Get document by ID
        
        Args:
            document_id: Document ID
            db: Database session
            user_id: Optional user ID for access control
        
        Returns:
            Document record or None if not found
        """
        try:
            query = db.query(Document).filter(Document.id == document_id)
            
            # Add user filter if provided
            if user_id:
                query = query.filter(Document.user_id == user_id)
            
            return query.first()
            
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            return None
    
    def get_user_documents(
        self,
        user_id: str,
        db: Session,
        limit: int = 20,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> List[Document]:
        """
        Get documents for a specific user
        
        Args:
            user_id: User ID
            db: Database session
            limit: Maximum number of documents to return
            offset: Number of documents to skip
            status_filter: Optional status filter ('pending', 'processing', 'completed', 'failed')
        
        Returns:
            List of document records
        """
        try:
            query = db.query(Document).filter(Document.user_id == user_id)
            
            # Add status filter if provided
            if status_filter:
                query = query.filter(Document.processing_status == status_filter)
            
            # Order by creation date (newest first) and apply pagination
            documents = query.order_by(Document.created_at.desc()).offset(offset).limit(limit).all()
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting user documents: {e}")
            return []
    
    def delete_document(self, document_id: str, db: Session, user_id: Optional[str] = None) -> bool:
        """
        Delete a document and its associated file
        
        Args:
            document_id: Document ID
            db: Database session
            user_id: Optional user ID for access control
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Get document
            document = self.get_document(document_id, db, user_id)
            if not document:
                logger.warning(f"Document not found for deletion: {document_id}")
                return False
            
            # Delete file from storage
            file_deleted = self.file_storage.delete_file(document.stored_filename)
            if not file_deleted:
                logger.warning(f"Failed to delete file: {document.stored_filename}")
            
            # Delete database record
            db.delete(document)
            db.commit()
            
            logger.info(f"Document deleted successfully: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            db.rollback()
            return False
    
    def get_document_stats(self, user_id: str, db: Session) -> Dict[str, Any]:
        """
        Get document statistics for a user
        
        Args:
            user_id: User ID
            db: Database session
        
        Returns:
            Dict containing document statistics
        """
        try:
            from sqlalchemy import func
            
            # Count documents by status
            status_counts = db.query(
                Document.processing_status,
                func.count(Document.id).label('count')
            ).filter(Document.user_id == user_id).group_by(Document.processing_status).all()
            
            # Total documents and file size
            total_stats = db.query(
                func.count(Document.id).label('total_documents'),
                func.sum(Document.file_size).label('total_size')
            ).filter(Document.user_id == user_id).first()
            
            stats = {
                "total_documents": total_stats.total_documents or 0,
                "total_file_size": total_stats.total_size or 0,
                "status_breakdown": {}
            }
            
            for status, count in status_counts:
                stats["status_breakdown"][status] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
            return {
                "total_documents": 0,
                "total_file_size": 0,
                "status_breakdown": {}
            }
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type based on file extension"""
        ext = Path(filename).suffix.lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        return mime_types.get(ext, 'application/octet-stream')


# Global document service instance
document_service = DocumentService()