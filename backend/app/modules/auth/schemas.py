from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username_or_email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=255)


class AuthUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_active: bool


class LoginResponse(BaseModel):
    message: str
    user: AuthUserResponse


class LogoutResponse(BaseModel):
    message: str


class MeResponse(BaseModel):
    user: AuthUserResponse
