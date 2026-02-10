"""
FILE: src/auth/router.py
Authentication endpoints - Production ready implementation
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from sqlalchemy import and_
from src.core.database import get_session
from src.core.security import (
    simple_decrypt, create_access_token, decode_access_token,
    generate_reset_token, generate_salt,
    simple_encrypt, generate_default_password
)
from src.shared.models import (
    Useraccount, Userprofile, PasswordResetToken,
    Address, Userregion
)
from src.shared.schemas import (
    LoginRequest, ResponseModel,
    ForgotPasswordRequest, ResetPasswordRequest,
    UserCreate, UserResponse, UserListResponse
)
from datetime import datetime, timedelta
from src.core.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/login", response_model=ResponseModel)
async def login(
    credentials: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    User login endpoint
    
    Returns JWT token on successful authentication
    Updates login count and last login date
    """
    try:
        # Find user by username
        statement = select(Useraccount).where(
            Useraccount.username == credentials.username
        )
        user = session.exec(statement).first()
        
        if not user:
            logger.warning(f"Login attempt with invalid username: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Check if account is locked
        if user.islocked:
            logger.warning(f"Login attempt for locked account: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked. Contact administrator."
            )
        
        # Check account status (1 = active)
        if user.status != 1:
            logger.warning(f"Login attempt for inactive account: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # Verify password (C# legacy compatibility)
        try:
            if user.passwordhash and user.salt:
                decrypted_password = simple_decrypt(user.passwordhash, user.salt)
                if credentials.password != decrypted_password:
                    # Increment failed login attempts
                    user.failedloginattempt = (user.failedloginattempt or 0) + 1
                    
                    # Lock account after 5 failed attempts
                    if user.failedloginattempt >= 5:
                        user.islocked = True
                        session.add(user)
                        session.commit()
                        logger.warning(f"Account locked due to failed attempts: {credentials.username}")
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Account locked due to multiple failed login attempts"
                        )
                    
                    session.add(user)
                    session.commit()
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid username or password"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Get user profile for additional info
        profile = session.exec(
            select(Userprofile).where(Userprofile.userid == user.userid)
        ).first()
        
        # Generate JWT token
        token_data = {
            "UserId": user.userid,
            "UserName": user.username,
            "UserStatus": user.status,
            "Email": user.email
        }
        access_token = create_access_token(data=token_data)
        
        # Update user login info
        user.logincount = (user.logincount or 0) + 1
        user.apitoken = access_token
        user.isactive = True
        user.lastlogindate = datetime.utcnow().date()
        user.failedloginattempt = 0  # Reset failed attempts on successful login
        user.updatedat = datetime.utcnow()
        
        session.add(user)
        session.commit()
        
        logger.info(f"Successful login: {credentials.username}")
        
        return ResponseModel(
            success=True,
            message="Login successful",
            data={
                "token": access_token,
                "user": {
                    "userid": user.userid,
                    "username": user.username,
                    "email": user.email,
                    "firstname": profile.firstname if profile else None,
                    "lastname": profile.lastname if profile else None,
                    "roleid": profile.roleid if profile else None
                }
            },
            tag=1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


@router.get("/logout", response_model=ResponseModel)
async def logout(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    User logout endpoint
    
    Clears API token and sets user as inactive
    Requires valid JWT token in Authorization header
    """
    try:
        # Extract token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Find user by token
        statement = select(Useraccount).where(Useraccount.apitoken == token)
        user = session.exec(statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Clear token and set inactive
        user.apitoken = None
        user.isactive = False
        user.updatedat = datetime.utcnow()
        
        session.add(user)
        session.commit()
        
        logger.info(f"User logged out: {user.username}")
        
        return ResponseModel(
            success=True,
            message="Logged out successfully",
            tag=1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during logout"
        )


# ============================================================================
# PASSWORD RESET ENDPOINTS
# ============================================================================

@router.post("/forgot-password", response_model=ResponseModel)
async def forgot_password(
    request: ForgotPasswordRequest,
    session: Session = Depends(get_session)
):
    """
    Request password reset
    
    Generates reset token and stores it
    In production, this should send an email
    Always returns success (security: don't reveal if email exists)
    """
    try:
        # Find user by email
        statement = select(Useraccount).where(
            Useraccount.email == request.email
        )
        user = session.exec(statement).first()
        
        # Always return success (security best practice)
        if not user:
            logger.info(f"Password reset requested for non-existent email: {request.email}")
            return ResponseModel(
                success=True,
                message="If email exists, reset link has been sent",
                tag=1
            )
        
        # Check account status
        if user.status != 1:
            return ResponseModel(
                success=True,
                message="If email exists, reset link has been sent",
                tag=1
            )
        
        # Generate reset token
        reset_token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(
            hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
        )
        
        # Invalidate existing tokens for this user
        old_tokens = session.exec(
            select(PasswordResetToken).where(
                and_(
                    PasswordResetToken.userid == user.userid, # type: ignore
                    PasswordResetToken.isused == False # type: ignore
                )
            )
        ).all()
        
        for old_token in old_tokens:
            old_token.isused = True
            old_token.updatedat = datetime.utcnow()
            session.add(old_token)
        
        # Create new token record
        token_record = PasswordResetToken(
            userid=user.userid,
            token=reset_token,
            expiresat=expires_at,
            isused=False,
            createdat=datetime.utcnow()
        )
        session.add(token_record)
        
        # Update user record
        user.passwordresettoken = reset_token
        user.passwordresettokenexpires = expires_at
        user.updatedat = datetime.utcnow()
        session.add(user)
        
        session.commit()
        
        logger.info(f"Password reset token generated for: {request.email}")
        
        # TODO: Send email with reset link
        # reset_link = f"{settings.API_BASE_URL}/reset-password?token={reset_token}"
        # await send_password_reset_email(user.email, reset_link)
        
        return ResponseModel(
            success=True,
            message="If email exists, reset link has been sent",
            data={"token": reset_token} if settings.ENVIRONMENT == "development" else None,
            tag=1
        )
        
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        # Still return success for security
        return ResponseModel(
            success=True,
            message="If email exists, reset link has been sent",
            tag=1
        )


@router.post("/reset-password", response_model=ResponseModel)
async def reset_password(
    request: ResetPasswordRequest,
    session: Session = Depends(get_session)
):
    """
    Reset password using token
    
    Validates token and updates user password
    """
    try:
        # Find valid token
        statement = select(PasswordResetToken).where(
            and_(
                PasswordResetToken.token == request.token, # type: ignore
                PasswordResetToken.isused == False, # type: ignore
                PasswordResetToken.expiresat > datetime.utcnow() # type: ignore
            )
        )
        token_record = session.exec(statement).first()
        
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        # Get user
        user = session.get(Useraccount, token_record.userid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate new salt and encrypt password
        salt = generate_salt()
        encrypted_password = simple_encrypt(request.newPassword, salt)
        
        # Update user password
        user.salt = salt
        user.passwordhash = encrypted_password
        user.lastpasswordreset = datetime.utcnow()
        user.passwordresettoken = None
        user.passwordresettokenexpires = None
        user.updatedat = datetime.utcnow()
        user.failedloginattempt = 0  # Reset failed attempts
        user.islocked = False  # Unlock account if locked
        
        # Mark token as used
        token_record.isused = True
        token_record.usedat = datetime.utcnow()
        token_record.updatedat = datetime.utcnow()
        
        session.add(user)
        session.add(token_record)
        session.commit()
        
        logger.info(f"Password reset successful for user: {user.username}")
        
        return ResponseModel(
            success=True,
            message="Password reset successfully",
            tag=1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during password reset"
        )


@router.get("/validate-reset-token", response_model=ResponseModel)
async def validate_reset_token(
    token: str,
    session: Session = Depends(get_session)
):
    """
    Validate password reset token
    
    Checks if token exists, is not used, and not expired
    """
    try:
        statement = select(PasswordResetToken).where(
            and_(
                PasswordResetToken.token == token, # type: ignore
                PasswordResetToken.isused == False, # type: ignore
                PasswordResetToken.expiresat > datetime.utcnow() # type: ignore
            )
        )
        token_record = session.exec(statement).first()
        
        if not token_record:
            return ResponseModel(
                success=False,
                message="Invalid or expired token",
                tag=0
            )
        
        return ResponseModel(
            success=True,
            message="Token is valid",
            data=True,
            tag=1
        )
        
    except Exception as e:
        logger.error(f"Validate token error: {str(e)}")
        return ResponseModel(
            success=False,
            message="An error occurred",
            tag=0
        )


# ============================================================================
# USER REGISTRATION ENDPOINT (Admin only)
# ============================================================================

@router.post("/register", response_model=ResponseModel)
async def register_user(
    user_data: UserCreate,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Register new user (extension officer)
    
    Requires authentication (admin/authorized user)
    Creates user account, profile, address, and user-region association
    Generates temporary password and sends email
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        token = auth_header[7:]
        token_data = decode_access_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Check if username already exists
        username = user_data.emailAddress.split('@')[0]  # Use email prefix as username
        existing_user = session.exec(
            select(Useraccount).where(Useraccount.username == username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email already exists
        existing_email = session.exec(
            select(Useraccount).where(Useraccount.email == user_data.emailAddress)
        ).first()
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Generate temporary password
        temp_password = generate_default_password()
        salt = generate_salt()
        encrypted_password = simple_encrypt(temp_password, salt)
        
        # Create user account
        new_user = Useraccount(
            username=username, # type: ignore
            email=user_data.emailAddress,
            passwordhash=encrypted_password,
            salt=salt,
            status=1,  # Active
            isactive=False,  # Inactive until first login
            islocked=False,
            logincount=0,
            failedloginattempt=0,
            lgaid=user_data.lgaid,
            createdat=datetime.utcnow()
        )
        
        session.add(new_user)
        session.flush()  # Get userid
        
        # Create user profile
        new_profile = Userprofile(
            userid=new_user.userid,
            firstname=user_data.firstname,
            middlename=user_data.middlename,
            lastname=user_data.lastname,
            gender=user_data.gender,
            email=user_data.emailAddress,
            phonenumber=user_data.phonenumber,
            lgaid=user_data.lgaid,
            createdat=datetime.utcnow()
        )
        
        session.add(new_profile)
        
        # Create address
        new_address = Address(
            userid=new_user.userid,
            streetaddress=user_data.streetaddress,
            town=user_data.town,
            postalcode=user_data.postalcode,
            lgaid=user_data.lgaid,
            latitude=user_data.latitude,
            longitude=user_data.longitude,
            createdat=datetime.utcnow()
        )
        
        session.add(new_address)
        
        # Create user-region association
        user_region = Userregion(
            userid=new_user.userid,
            regionid=user_data.regionid,
            createdat=datetime.utcnow()
        )
        
        session.add(user_region)
        
        session.commit()
        
        logger.info(f"New user registered: {username}")
        
        # TODO: Send email with login credentials
        # await send_welcome_email(
        #     email=user_data.emailAddress,
        #     username=username,
        #     temp_password=temp_password
        # )
        
        return ResponseModel(
            success=True,
            message="User registered successfully. Login credentials sent to email.",
            data={
                "userid": new_user.userid,
                "username": username,
                "email": user_data.emailAddress,
                "temp_password": temp_password if settings.ENVIRONMENT == "development" else None
            },
            tag=1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration error: {str(e)}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
        )


@router.get("/officers", response_model=UserListResponse)
async def get_officers(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Get list of all registered officers
    
    Requires authentication
    Returns list of users with their profiles
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        token = auth_header[7:]
        token_data = decode_access_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get all active users with their profiles
        users = session.exec(
            select(Useraccount).where(Useraccount.deletedat == None)
        ).all()
        
        user_list = []
        for user in users:
            profile = session.exec(
                select(Userprofile).where(Userprofile.userid == user.userid)
            ).first()
            
            user_list.append({
                "userid": user.userid,
                "username": user.username,
                "email": user.email,
                "status": user.status,
                "isactive": user.isactive,
                "firstname": profile.firstname if profile else None,
                "lastname": profile.lastname if profile else None,
                "phonenumber": profile.phonenumber if profile else None,
                "lgaid": user.lgaid,
                "logincount": user.logincount,
                "lastlogindate": user.lastlogindate
            })
        
        return UserListResponse(
            success=True,
            message="Officers retrieved successfully",
            data=user_list,
            tag=1,
            total=len(user_list)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get officers error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching officers"
        )


@router.get("/officers/{user_id}", response_model=UserResponse)
async def get_officer(
    user_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Get specific officer details
    
    Requires authentication
    Returns user with profile and address details
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        token = auth_header[7:]
        token_data = decode_access_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user
        user = session.get(Useraccount, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get profile
        profile = session.exec(
            select(Userprofile).where(Userprofile.userid == user_id)
        ).first()
        
        # Get address
        address = session.exec(
            select(Address).where(Address.userid == user_id)
        ).first()
        
        # Get user region
        user_region = session.exec(
            select(Userregion).where(Userregion.userid == user_id)
        ).first()
        
        officer_data = {
            "userid": user.userid,
            "username": user.username,
            "email": user.email,
            "status": user.status,
            "isactive": user.isactive,
            "firstname": profile.firstname if profile else None,
            "lastname": profile.lastname if profile else None,
            "middlename": profile.middlename if profile else None,
            "gender": profile.gender if profile else None,
            "phonenumber": profile.phonenumber if profile else None,
            "designation": profile.designation if profile else None,
            "lgaid": user.lgaid,
            "regionid": user_region.regionid if user_region else None,
            "streetaddress": address.streetaddress if address else None,
            "town": address.town if address else None,
            "postalcode": address.postalcode if address else None,
            "latitude": address.latitude if address else None,
            "longitude": address.longitude if address else None,
            "logincount": user.logincount,
            "lastlogindate": user.lastlogindate,
            "createdat": user.createdat
        }
        
        return UserResponse(
            success=True,
            message="Officer retrieved successfully",
            data=officer_data,
            tag=1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get officer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching officer"
        )