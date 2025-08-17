"""
Main FastAPI application for Legal Statute Analysis System
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.logging import setup_logging
from .core.database_init import initialize_database
from .api.auth import router as auth_router
from .api.documents import router as documents_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan events for startup and shutdown
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    try:
        # Initialize database
        initialize_database()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Application shutdown completed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="國考法律題型分析系統 - 結合生成式 AI 和資訊系統整合的法律學習平台",
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
if settings.debug:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routers
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(documents_router, prefix=settings.api_prefix)


# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@app.get(f"{settings.api_prefix}/")
async def api_root():
    """API root endpoint"""
    return {
        "message": f"{settings.app_name} API",
        "version": settings.app_version,
        "api_prefix": settings.api_prefix,
        "endpoints": {
            "auth": f"{settings.api_prefix}/auth",
            "documents": f"{settings.api_prefix}/documents",
            "docs": "/docs",
            "health": "/health",
            "status": f"{settings.api_prefix}/status"
        }
    }


@app.get(f"{settings.api_prefix}/status")
async def development_status():
    """Development status and progress endpoint"""
    return {
        "project": settings.app_name,
        "version": settings.app_version,
        "development_phase": "第一迭代 MVP 開發",
        "completion_percentage": "80%",
        "current_task": "文件處理服務開發",
        "completed_modules": [
            {
                "name": "基礎環境配置",
                "status": "✅ 完成",
                "completion_date": "2025-08-17"
            },
            {
                "name": "資料庫架構",
                "status": "✅ 完成",
                "completion_date": "2025-08-17",
                "details": "4張核心表 (users, documents, legal_articles, question_analyses)"
            },
            {
                "name": "用戶認證系統",
                "status": "✅ 完成",
                "completion_date": "2025-08-17",
                "details": "JWT 認證、密碼加密、API 端點"
            },
            {
                "name": "FastAPI 基礎架構",
                "status": "✅ 完成",
                "completion_date": "2025-08-17",
                "details": "CORS、生命週期、異常處理"
            }
        ],
        "in_progress_modules": [
            {
                "name": "文件處理服務",
                "status": "🔄 開發中",
                "progress": "90%",
                "estimated_completion": "2025-08-18"
            }
        ],
        "planned_modules": [
            {
                "name": "AI 分析服務",
                "status": "⏳ 規劃中",
                "estimated_start": "2025-08-18"
            },
            {
                "name": "知識庫服務",
                "status": "⏳ 規劃中",
                "estimated_start": "2025-08-19"
            },
            {
                "name": "單元測試",
                "status": "⏳ 規劃中",
                "estimated_start": "2025-08-20"
            }
        ],
        "technical_stack": {
            "backend": "Python 3.11 + FastAPI + SQLAlchemy",
            "database": "PostgreSQL + Docker",
            "authentication": "JWT + bcrypt",
            "dependency_management": "Poetry",
            "ai_frameworks": "LangChain + OpenAI (規劃中)"
        },
        "api_endpoints": {
            "implemented": [
                "POST /api/v1/auth/register",
                "POST /api/v1/auth/login", 
                "GET /api/v1/auth/verify-token",
                "GET /api/v1/auth/profile",
                "PUT /api/v1/auth/profile",
                "GET /health"
            ],
            "planned": [
                "POST /api/v1/analysis/question",
                "GET /api/v1/knowledge/search"
            ],
            "documents": [
                "POST /api/v1/documents/upload",
                "GET /api/v1/documents/",
                "GET /api/v1/documents/{id}",
                "GET /api/v1/documents/{id}/content",
                "POST /api/v1/documents/{id}/process",
                "DELETE /api/v1/documents/{id}",
                "GET /api/v1/documents/stats/summary"
            ]
        },
        "last_updated": "2025-08-17T15:23:00Z"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.reload,
        workers=settings.workers if not settings.reload else 1,
        log_level=settings.log_level.lower()
    )