from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    EmailVerificationRequest,
    ResendVerificationRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChange,
)
from app.schemas.token import RefreshTokenRequest, RefreshTokenResponse
from app.services.auth import auth_service
from app.repository.user import user_crud
from app.repository.token import refresh_token_crud

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ========== register and login ==========

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register new user
    
    After registration, an email verification email will be sent. Users need to verify their email before they can login.
    
    Args:
        user_data: user register data
        db: Database session
        
    Returns:
        Create user information
        
    Raises:
        HTTPException: Username or email already exists
    """
    try:
        user = await auth_service.register_user(db, user_data, send_verification=True)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """User login
    
    After successful login, return access token and refresh token.
    User must have verified their email to login.
    
    Args:
        user_login: login credentials
        request: request object
        db: Database session
        
    Returns:
        access token and refresh token
        
    Raises:
        HTTPException: authentication failed or email not verified
    """
    # Get device information
    user_agent = request.headers.get("User-Agent", "Unknown")
    ip_address = request.client.host if request.client else None
    
    # Prefer to use email, otherwise use username
    login_identifier = user_login.email or user_login.username
    
    token = await auth_service.login_user(
        db,
        login_identifier,
        user_login.password,
        device_name=user_agent[:100] if user_agent else None,
        device_type="web",
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password, or email not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


@router.post("/logout")
async def logout(
    refresh_token_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """user logout
    
    Revoke specified refresh token.
    
    Args:
        refresh_token_request: refresh token request
        db: Database session
        
    Returns:
        success message
    """
    success = await auth_service.logout_user(db, refresh_token_request.refresh_token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    
    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout all devices
    
    Revoke all refresh tokens for current user.
    
    Args:
        current_user: current user
        db: Database session
        
    Returns:
        Revoke token quantity
    """
    count = await auth_service.logout_all_devices(db, current_user.id)
    return {"message": f"Successfully logged out from {count} devices"}


# ========== token refresh ==========

@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_token_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """refresh access token
    
    use refresh token Get new access token。
    
    Args:
        refresh_token_request: refresh token request
        db: Database session
        
    Returns:
        new access token
        
    Raises:
        HTTPException: refresh token invalid or already expired
    """
    access_token = await auth_service.refresh_access_token(db, refresh_token_request.refresh_token)
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"access_token": access_token, "token_type": "bearer"}


# ========== EmailValidate ==========

@router.post("/verify-email")
async def verify_email(
    verification: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify Email
    
    Use verification code to verify user email.
    
    Args:
        verification: Email Validate request
        db: Database session
        
    Returns:
        success message
        
    Raises:
        HTTPException: verification code invalid or already expired
    """
    # find user
    user = await user_crud.get_by_email(db, verification.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify Email
    success = await auth_service.verify_email(db, user.id, verification.code)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
    
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Resend verification email
    
    Args:
        request: Resend verification request
        db: Database session
        
    Returns:
        success message
        
    Raises:
        HTTPException: user does not exist or email already verified
    """
    # find user
    user = await user_crud.get_by_email(db, request.email)
    if not user:
        # For security, return success even if user does not exist
        return {"message": "If the email exists, a verification code has been sent"}
    
    # Check whether already Validate
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # send Validate email
    await auth_service.send_verification_email(db, user)
    
    return {"message": "Verification email sent"}


# ========== Password reset ==========

@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset
    
    Send password reset email to user's email.
    
    Args:
        request: Password reset request
        db: Database session
        
    Returns:
        success message
    """
    await auth_service.request_password_reset(db, request.email)
    
    # For security, always return success message
    return {"message": "If the email exists, a password reset code has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Reset password
    
    Use verification code to reset password.
    
    Args:
        reset_data: Password reset confirm data
        db: Database session
        
    Returns:
        success message
        
    Raises:
        HTTPException: verification code invalid or already expired
    """
    success = await auth_service.reset_password(
        db,
        reset_data.email,
        reset_data.code,
        reset_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code"
        )
    
    return {"message": "Password reset successfully"}


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change password
    
    User changes their own password (requires old password).
    
    Args:
        password_data: Password modify data
        current_user: current user
        db: Database session
        
    Returns:
        success message
        
    Raises:
        HTTPException: old Password error
    """
    # Validate old Password
    user = await user_crud.authenticate(db, current_user.username, password_data.old_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Change password
    await user_crud.change_password(db, current_user.id, password_data.new_password)
    
    # Revoke all refresh tokens (force re-login)
    await refresh_token_crud.revoke_user_tokens(db, current_user.id)
    
    return {"message": "Password changed successfully. Please login again."}


# ========== Device management ==========

@router.get("/devices", response_model=list[RefreshTokenResponse])
async def list_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all login devices
    
    List all active login devices for current user.
    
    Args:
        current_user: current user
        db: Database session
        
    Returns:
        Device list
    """
    tokens = await refresh_token_crud.get_user_tokens(db, current_user.id, include_revoked=False)
    return tokens

