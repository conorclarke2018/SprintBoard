import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import UserRole

USERNAME_PATTERN = re.compile(r"^[a-z0-9_]+$")
MAX_PASSWORD_BYTES = 72  # bcrypt's limit


def normalise_username(value: object) -> object:
    return value.strip().lower() if isinstance(value, str) else value


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8)

    _normalise_username = field_validator("username", mode="before")(normalise_username)

    @field_validator("username")
    @classmethod
    def check_username_characters(cls, value: str) -> str:
        if not USERNAME_PATTERN.match(value):
            raise ValueError("Use only letters, numbers and underscores")
        return value

    @field_validator("password")
    @classmethod
    def check_password_length(cls, value: str) -> str:
        if len(value.encode()) > MAX_PASSWORD_BYTES:
            raise ValueError("Password is too long (maximum 72 characters)")
        return value


class UserLogin(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)

    _normalise_username = field_validator("username", mode="before")(normalise_username)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: UserRole
    is_approved: bool


class AdminUserRead(UserRead):
    """Extra details shown on the admin's user management page."""

    created_at: datetime
    project_count: int


class RoleUpdate(BaseModel):
    role: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
