from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    is_locked: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserList(BaseModel):
    users: list[UserPublic]
    total: int
