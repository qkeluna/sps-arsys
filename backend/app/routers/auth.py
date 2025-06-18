"""
Authentication router for user login, registration, and user management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import (
    LoginRequest, RegisterRequest, TokenResponse, 
    UserResponse, UserUpdate, MessageResponse
)
from ..services.auth import (
    AuthService, get_current_user, get_current_active_user,
    create_access_token_response
)
from ..models import User, UserRole


router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        # Create user
        user = AuthService.create_user(
            db=db,
            user_create=user_data
        )
        
        # Return access token
        return create_access_token_response(user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login user with email and password"""
    user = AuthService.authenticate_user(
        db=db,
        email=login_data.email,
        password=login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    return create_access_token_response(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/promote-to-studio-owner", response_model=MessageResponse)
async def promote_to_studio_owner(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Promote current user to studio owner role"""
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only customers can be promoted to studio owners"
        )
    
    current_user.role = UserRole.STUDIO_OWNER
    db.commit()
    
    return MessageResponse(
        message="Successfully promoted to studio owner! You can now create and manage studios.",
        success=True
    )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify user email (simplified implementation)"""
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # In a real implementation, you would:
    # 1. Send verification email with token
    # 2. Verify token from email link
    # For now, we'll just mark as verified
    
    current_user.is_verified = True
    db.commit()
    
    return MessageResponse(
        message="Email verified successfully!",
        success=True
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """Logout user (client-side token removal)"""
    # In a stateless JWT system, logout is typically handled client-side
    # by removing the token. For enhanced security, you might:
    # 1. Maintain a blacklist of tokens
    # 2. Use shorter token expiry times
    # 3. Implement refresh tokens
    
    return MessageResponse(
        message="Logged out successfully",
        success=True
    ) 