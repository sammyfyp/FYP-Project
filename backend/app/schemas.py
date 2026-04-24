from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def normalize_phone(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = "".join(value.split())
    return normalized if normalized else None


class UserEntryRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    emergency_number: str | None = Field(default=None, max_length=50)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Name is required.")
        return trimmed

    @field_validator("emergency_number")
    @classmethod
    def validate_emergency_number(cls, value: str | None) -> str | None:
        return normalize_phone(value)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    emergency_number: str | None
    created_at: datetime


class UserEntryResponse(BaseModel):
    inserted: bool
    user: UserOut


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class AdminInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminInfo


class AdminUsersResponse(BaseModel):
    users: list[UserOut]


class AdminStatsResponse(BaseModel):
    total_users: int
    users_with_emergency_number: int
    users_without_emergency_number: int
