"""
JWT Authentication & Authorization

HIPAA-compliant authentication system with audit logging.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from core.config import settings
from core.logging import get_logger

logger = get_logger()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ============================================================================
# MODELS
# ============================================================================

class TokenData(BaseModel):
    """JWT token data"""
    user_id: str
    username: str
    roles: list[str]
    exp: datetime


class User(BaseModel):
    """User model"""
    user_id: str
    username: str
    email: str
    full_name: str
    roles: list[str]
    is_active: bool = True
    created_at: datetime


class UserInDB(User):
    """User model with hashed password"""
    hashed_password: str


# ============================================================================
# PASSWORD UTILITIES
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


# ============================================================================
# JWT UTILITIES
# ============================================================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token

    Args:
        data: Data to encode in token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate JWT token

    Args:
        token: JWT token string

    Returns:
        Token data

    Raises:
        HTTPException: If token is invalid
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        roles: list = payload.get("roles", [])
        exp: datetime = datetime.fromtimestamp(payload.get("exp"))

        if user_id is None:
            raise credentials_exception

        token_data = TokenData(
            user_id=user_id,
            username=username,
            roles=roles,
            exp=exp
        )

        return token_data

    except JWTError:
        raise credentials_exception


# ============================================================================
# USER AUTHENTICATION
# ============================================================================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get current authenticated user

    Dependency for protected endpoints.
    """

    token_data = decode_access_token(token)

    # In production: fetch from database
    # For now, reconstruct from token
    user = User(
        user_id=token_data.user_id,
        username=token_data.username,
        email=f"{token_data.username}@hospital.com",
        full_name=token_data.username.title(),
        roles=token_data.roles,
        is_active=True,
        created_at=datetime.utcnow()
    )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Audit log
    logger.audit(
        action="user_authentication",
        user_id=user.user_id,
        resource=f"api_access",
        outcome="success",
        username=user.username
    )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ============================================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================================

class RoleChecker:
    """
    Dependency for checking user roles

    Usage:
        @app.get("/admin")
        async def admin_only(user: User = Depends(RoleChecker(["admin"]))):
            ...
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        """Check if user has required role"""

        if not any(role in self.allowed_roles for role in user.roles):
            logger.audit(
                action="unauthorized_access_attempt",
                user_id=user.user_id,
                resource=f"roles:{','.join(self.allowed_roles)}",
                outcome="failure",
                username=user.username
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required role. Required: {self.allowed_roles}"
            )

        return user


# Predefined role checkers
require_physician = RoleChecker(["physician", "admin"])
require_nurse = RoleChecker(["nurse", "physician", "admin"])
require_admin = RoleChecker(["admin"])


# ============================================================================
# MOCK USER DATABASE (for development)
# ============================================================================

# In production, this would be in the database
MOCK_USERS_DB = {
    "dr.smith": UserInDB(
        user_id="user-001",
        username="dr.smith",
        email="smith@hospital.com",
        full_name="Dr. John Smith",
        roles=["physician", "admin"],
        hashed_password=get_password_hash("password123"),  # NEVER in production!
        created_at=datetime.utcnow()
    ),
    "nurse.johnson": UserInDB(
        user_id="user-002",
        username="nurse.johnson",
        email="johnson@hospital.com",
        full_name="Sarah Johnson",
        roles=["nurse"],
        hashed_password=get_password_hash("password123"),
        created_at=datetime.utcnow()
    )
}


async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate user with username and password

    Args:
        username: Username
        password: Plain text password

    Returns:
        User if authenticated, None otherwise
    """

    user = MOCK_USERS_DB.get(username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
