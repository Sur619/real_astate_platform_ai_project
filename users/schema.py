import re
import uuid
from pydantic import BaseModel, EmailStr
from pydantic.v1 import validator
from typing import Optional

# Update to allow spaces and apostrophes in names
LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-\s']+$")


class UserBase(BaseModel):
    name: str
    email: EmailStr

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise ValueError("Name should contain only letters, spaces, hyphens, and apostrophes")
        return value


class UserCreate(UserBase):
    password: str


class GroupSchema(BaseModel):
    group_id: uuid.UUID
    name: str


class ShowUser(UserBase):
    user_id: uuid.UUID
    is_active: bool
    groups: list[GroupSchema] = []

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class Token(BaseModel):
    access_token: str  # Add missing field
    token_type: str
    refresh_token: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str