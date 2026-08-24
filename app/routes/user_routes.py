import logging

from fastapi import APIRouter, HTTPException, status

from app.models.user_dto import (
    LoginRequest,
    LoginResponse,
    RegistrationRequest,
    RegistrationResponse,
)
from app.services.user_service import user_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Users"])


@router.post("/admin/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest) -> LoginResponse:
    """Authenticate the configured administrator account."""
    authenticated_admin = user_service.authenticate_admin(request.username, request.password)
    if authenticated_admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin username or password",
        )

    logger.info("Admin login successful for username=%s", authenticated_admin.username)
    return LoginResponse(
        success=True,
        message="Admin login successful",
        user={"username": authenticated_admin.username, "role": "admin"},
    )


@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegistrationRequest) -> RegistrationResponse:
    """Register a new user and return a safe user summary."""
    registered_user = user_service.register_user(
        request.email,
        request.password,
        request.first_name,
        request.last_name,
        request.phone_number,
    )
    if registered_user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists or registration failed",
        )

    logger.info("User registered with email=%s", registered_user.username)
    return RegistrationResponse(
        success=True,
        message="Registration successful",
        user={"user_id": registered_user.user_id, "username": registered_user.username},
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """Authenticate a user and return a safe user summary."""
    authenticated_user = user_service.authenticate_user(request.username, request.password)
    if authenticated_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    logger.info("Login successful for username=%s", authenticated_user.username)
    return LoginResponse(
        success=True,
        message="Login successful",
        user={"user_id": authenticated_user.user_id, "username": authenticated_user.username},
    )