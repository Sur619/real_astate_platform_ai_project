from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jwt import ExpiredSignatureError, InvalidTokenError
import jwt
import logging
from configs.settings import Settings

settings = Settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub")
    except ExpiredSignatureError:
        logger.error("JWT decode error: Token expired")
        return None
    except InvalidTokenError as e:
        logger.error(f"JWT decode error: {e}")
        return None


def create_refresh_token(data: dict):
    expires = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    data.update({"exp": expires})
    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)