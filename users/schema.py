import re
import uuid
from pydantic import BaseModel, EmailStr, validator


LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise ValueError("name should contains only letters")
        return value


class ShowUser(UserBase):
    user_id: uuid.UUID
    is_active: bool

    class Config:
        from_attributes = True  # Позволяет создавать модель из ORM-объектов


class Token(BaseModel):
    access_token: str
    token_type: str
