from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from enum import Enum


class RoleEnum(str, Enum):
    Admin = "Admin"
    Manager = "Manager"
    User = "User"


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.User

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    role: RoleEnum
    is_active: bool

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[RoleEnum] = None
