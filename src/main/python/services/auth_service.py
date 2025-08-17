"""
Authentication service for user registration, login, and JWT token management
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid

from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.user import User

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


class AuthService:
    """Authentication service for handling user authentication and authorization"""
    
    def __init__(self):
        self.pwd_context = pwd_context
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password
        
        Args:
            plain_password: The plain text password
            hashed_password: The hashed password from database
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """
        Hash a plain password
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing password"
            )
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Data to encode in the token
            expires_delta: Custom expiration time
            
        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating access token"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Dict[str, Any]: Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get user by email address
        
        Args:
            db: Database session
            email: User email address
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Database error getting user by email: {e}")
            return None
    
    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User ID (UUID as string)
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        try:
            user_uuid = uuid.UUID(user_id)
            return db.query(User).filter(User.id == user_uuid).first()
        except (ValueError, Exception) as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            Optional[User]: User object if authentication successful, None otherwise
        """
        user = self.get_user_by_email(db, email)
        if not user:
            logger.warning(f"Authentication failed: user not found for email {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"Authentication failed: user account inactive for email {email}")
            return None
        
        if not self.verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password for email {email}")
            return None
        
        # Update last login time
        try:
            user.last_login_at = datetime.utcnow()
            db.commit()
            logger.info(f"User {email} authenticated successfully")
        except Exception as e:
            logger.error(f"Error updating last login time: {e}")
            db.rollback()
        
        return user
    
    def create_user(self, db: Session, email: str, password: str, full_name: Optional[str] = None) -> User:
        """
        Create a new user account
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            full_name: User's full name
            
        Returns:
            User: Created user object
            
        Raises:
            HTTPException: If user already exists or creation fails
        """
        # Check if user already exists
        existing_user = self.get_user_by_email(db, email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = self.get_password_hash(password)
        
        # Create user
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            subscription_type="free",
            is_active=True,
            is_admin=False
        )
        
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"New user created: {email}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user account"
            )
    
    def get_current_user(self, db: Session, credentials: HTTPAuthorizationCredentials) -> User:
        """
        Get current user from JWT token
        
        Args:
            db: Database session
            credentials: HTTP Authorization credentials
            
        Returns:
            User: Current user object
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        token = credentials.credentials
        payload = self.verify_token(token)
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user = self.get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
    
    def require_admin(self, user: User) -> User:
        """
        Require that the user has admin privileges
        
        Args:
            user: User object to check
            
        Returns:
            User: The user object if admin
            
        Raises:
            HTTPException: If user is not admin
        """
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        return user


# Global auth service instance
auth_service = AuthService()