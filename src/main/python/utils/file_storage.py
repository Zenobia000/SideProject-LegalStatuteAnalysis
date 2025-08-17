"""
File storage utility for handling uploaded documents
"""
import os
import uuid
from pathlib import Path
from typing import Optional, BinaryIO
import shutil
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


class FileStorage:
    """File storage manager for uploaded documents"""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.max_file_size = settings.max_file_size
        self.allowed_extensions = settings.allowed_extensions.split(',')
        
        # Create upload directory if it doesn't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"File storage initialized: {self.upload_dir}")
    
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        if not filename:
            return False
        
        file_ext = Path(filename).suffix.lower()
        return file_ext in self.allowed_extensions
    
    def check_file_size(self, file_size: int) -> bool:
        """Check if file size is within limits"""
        return file_size <= self.max_file_size
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename while preserving extension"""
        file_ext = Path(original_filename).suffix
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_ext}"
    
    def save_file(self, file: BinaryIO, original_filename: str) -> tuple[str, str]:
        """
        Save uploaded file to storage
        
        Returns:
            tuple[str, str]: (unique_filename, file_path)
        """
        if not self.is_allowed_file(original_filename):
            raise ValueError(f"File type not allowed: {Path(original_filename).suffix}")
        
        # Generate unique filename
        unique_filename = self.generate_unique_filename(original_filename)
        file_path = self.upload_dir / unique_filename
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file, buffer)
            
            # Verify file size after saving
            file_size = file_path.stat().st_size
            if not self.check_file_size(file_size):
                file_path.unlink()  # Delete the file
                raise ValueError(f"File size exceeds limit: {file_size} bytes")
            
            logger.info(f"File saved successfully: {unique_filename}")
            return unique_filename, str(file_path)
            
        except Exception as e:
            # Clean up on error
            if file_path.exists():
                file_path.unlink()
            logger.error(f"Error saving file: {e}")
            raise
    
    def get_file_path(self, filename: str) -> Optional[Path]:
        """Get full path to stored file"""
        file_path = self.upload_dir / filename
        return file_path if file_path.exists() else None
    
    def delete_file(self, filename: str) -> bool:
        """Delete file from storage"""
        file_path = self.upload_dir / filename
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return False
    
    def get_file_info(self, filename: str) -> Optional[dict]:
        """Get file information"""
        file_path = self.get_file_path(filename)
        if not file_path:
            return None
        
        try:
            stat = file_path.stat()
            return {
                "filename": filename,
                "size": stat.st_size,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime,
                "extension": file_path.suffix,
                "path": str(file_path)
            }
        except Exception as e:
            logger.error(f"Error getting file info for {filename}: {e}")
            return None


# Global file storage instance
file_storage = FileStorage()