from pydantic import BaseModel, ConfigDict


class RegistrationRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str | None = None
    phone_number: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "new.customer@example.com",
                "password": "StrongPassword123",
                "first_name": "New",
                "last_name": "Customer",
                "phone_number": "9876543210",
            }
        }
    )


class LoginRequest(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"username": "admin", "password": "admin123"}}
    )


class LoginResponse(BaseModel):
    success: bool
    message: str
    user: dict[str, str | int] | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Login successful",
                "user": {"username": "admin"},
            }
        }
    )


class RegistrationResponse(LoginResponse):
    pass