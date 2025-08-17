"""
Authentication API endpoints for user registration, login, and profile management
"""
import logging
from typing import Any, Dict, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.user import User
from ..services.auth_service import auth_service, security

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/auth", tags=["authentication"])


# Pydantic models for request/response
class UserRegister(BaseModel):
    """User registration request model"""
    email: EmailStr
    password: str
    full_name: str = None
    
    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfile(BaseModel):
    """User profile response model"""
    id: str
    email: str
    full_name: str = None
    subscription_type: str
    is_active: bool
    created_at: str
    last_login_at: Union[str, None] = None
    
    @classmethod
    def from_orm(cls, user: User) -> "UserProfile":
        """Create UserProfile from User model"""
        return cls(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            subscription_type=user.subscription_type,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None
        )
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """User profile update request model"""
    full_name: str = None


# Authentication dependencies
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    return auth_service.get_current_user(db, credentials)


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin user"""
    return auth_service.require_admin(current_user)


# API Endpoints
@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> UserProfile:
    """
    Register a new user account
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        UserProfile: Created user profile
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        user = auth_service.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        logger.info(f"User registered successfully: {user.email}")
        return UserProfile(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            subscription_type=user.subscription_type,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Token:
    """
    Authenticate user and return access token
    
    Args:
        user_credentials: User login credentials
        db: Database session
        
    Returns:
        Token: Access token and metadata
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        user = auth_service.authenticate_user(
            db=db,
            email=user_credentials.email,
            password=user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        logger.info(f"User logged in successfully: {user.email}")
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserProfile:
    """
    Get current user's profile information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserProfile: User profile data
    """
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        subscription_type=current_user.subscription_type,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
        last_login_at=current_user.last_login_at.isoformat() if current_user.last_login_at else None
    )


@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserProfile:
    """
    Update current user's profile information
    
    Args:
        profile_update: Profile update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserProfile: Updated user profile
        
    Raises:
        HTTPException: If update fails
    """
    try:
        # Update user profile
        if profile_update.full_name is not None:
            current_user.full_name = profile_update.full_name
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"User profile updated: {current_user.email}")
        return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        subscription_type=current_user.subscription_type,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
        last_login_at=current_user.last_login_at.isoformat() if current_user.last_login_at else None
    )
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Log out current user (invalidate token on client side)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict[str, str]: Success message
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}


@router.get("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Verify if the current token is valid
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict[str, Any]: Token verification result
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "email": current_user.email,
        "is_active": current_user.is_active
    }


# Admin-only endpoints
@router.get("/admin/users", response_model=list[UserProfile])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> list[UserProfile]:
    """
    Get list of all users (admin only)
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_admin: Current admin user
        db: Database session
        
    Returns:
        list[UserProfile]: List of user profiles
    """
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return [
            UserProfile(
                id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                subscription_type=user.subscription_type,
                is_active=user.is_active,
                created_at=user.created_at.isoformat(),
                last_login_at=user.last_login_at.isoformat() if user.last_login_at else None
            )
            for user in users
        ]
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )