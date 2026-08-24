from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.models.user_dto import LoginRequest, RegistrationRequest
from app.routes.user_routes import login, register


@pytest.mark.asyncio
@patch("app.routes.user_routes.user_service.register_user")
async def test_register_success(mock_register_user):
    mock_register_user.return_value = type("User", (), {"username": "new@example.com"})()
    response = await register(
        RegistrationRequest(
            email="new@example.com",
            password="StrongPassword123",
            first_name="New",
        )
    )

    assert response.success is True
    assert response.message == "Registration successful"
    assert response.user == {"username": "new@example.com"}
    mock_register_user.assert_called_once_with(
        "new@example.com", "StrongPassword123", "New", None, None
    )


@pytest.mark.asyncio
@patch("app.routes.user_routes.user_service.register_user", return_value=None)
async def test_register_duplicate_email(mock_register_user):
    with pytest.raises(HTTPException) as exc_info:
        await register(
            RegistrationRequest(
                email="existing@example.com",
                password="StrongPassword123",
                first_name="Existing",
            )
        )

    assert exc_info.value.status_code == 409
    mock_register_user.assert_called_once_with(
        "existing@example.com", "StrongPassword123", "Existing", None, None
    )


@pytest.mark.asyncio
@patch("app.routes.user_routes.user_service.authenticate_user")
async def test_login_success(mock_authenticate_user):
    mock_authenticate_user.return_value = type("User", (), {"username": "admin"})()
    response = await login(LoginRequest(username="admin", password="admin123"))

    assert response.success is True
    assert response.message == "Login successful"
    assert response.user == {"username": "admin"}
    mock_authenticate_user.assert_called_once_with("admin", "admin123")


@pytest.mark.asyncio
@patch("app.routes.user_routes.user_service.authenticate_user", return_value=None)
async def test_login_invalid_credentials(mock_authenticate_user):
    with pytest.raises(HTTPException) as exc_info:
        await login(LoginRequest(username="wrong", password="badpass"))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid username or password"
    mock_authenticate_user.assert_called_once_with("wrong", "badpass")
