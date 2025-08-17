"""
Configuration module for Legal Statute Analysis System
"""
import os
from functools import lru_cache
from typing import List, Optional

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "國考法律題型分析系統"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "production"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Security
    secret_key: str
    access_token_expire_minutes: int = 1440  # 24 hours
    algorithm: str = "HS256"
    
    # Database
    database_url: str
    database_echo: bool = False
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 4000
    
    # File Storage
    upload_dir: str = "data/uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: str = ".pdf"
    
    # OCR
    ocr_engine: str = "paddleocr"
    ocr_language: str = "ch_tra"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "logs/app.log"
    
    # Development
    reload: bool = False
    workers: int = 1
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if not v:
            raise ValueError("SECRET_KEY must be set")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("openai_api_key")
    def validate_openai_api_key(cls, v):
        if not v:
            raise ValueError("OPENAI_API_KEY must be set")
        return v
    
    @validator("upload_dir")
    def validate_upload_dir(cls, v):
        # Ensure upload directory exists
        os.makedirs(v, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()