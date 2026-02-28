"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RefreshTokenRequest,
)
from auth.security import (
    create_access_token,
    create_refresh_token,
    get_current_user_id,
)
from auth.service import AuthService
from models.user import UserResponse, UserRole

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest):
    """
    Register a new user

    - **email**: User email address
    - **password**: User password (min 8 characters)
    - **full_name**: User's full name
    """
    try:
        from models.user import UserCreate
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=UserRole.USER,
            is_active=True,
        )
        user = await AuthService.create_user(user_create)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate user and return tokens

    - **email**: User email address
    - **password**: User password
    """
    user = await AuthService.authenticate_user(credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create tokens
    access_token = create_access_token(
        data={
            "sub": user.id,
            "email": user.email,
            "role": user.role.value
        }
    )
    refresh_token = create_refresh_token(
        data={
            "sub": user.id,
            "email": user.email,
            "role": user.role.value
        }
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
        }
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(token_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token

    - **refresh_token**: Valid refresh token
    """
    from auth.security import decode_token

    try:
        payload = decode_token(token_data.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = payload.get("sub")
        user = await AuthService.get_user_by_id(user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new tokens
        access_token = create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "role": user.role.value
            }
        )
        new_refresh_token = create_refresh_token(
            data={
                "sub": user.id,
                "email": user.email,
                "role": user.role.value
            }
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
            }
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get current user information

    Requires valid access token
    """
    user = await AuthService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)


@router.post("/init-admin", response_model=UserResponse)
async def initialize_admin():
    """
    Initialize default admin user

    Creates admin user if none exists.
    Default credentials: admin@aidatalabs.ai / admin123
    """
    admin = await AuthService.create_default_admin()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin already exists"
        )
    return UserResponse.model_validate(admin)
