import re
import uuid
from pydantic import BaseModel, EmailStr, field_validator, HttpUrl
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

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class GroupSchema(BaseModel):
    group_id: uuid.UUID
    name: str


class ShowUser(UserBase):
    user_id: uuid.UUID
    is_active: bool
    groups: list[GroupSchema] = []

    avatar_url: Optional[HttpUrl]

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
