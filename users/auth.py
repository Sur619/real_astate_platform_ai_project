from datetime import timedelta
import logging

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from pydantic.v1 import validator

from users.repositories import UserRepository, get_user_repository
from users.schema import Token, LoginResponse
from users.security import verify_password, create_access_token, decode_access_token, create_refresh_token
from configs.settings import Settings

auth_router = APIRouter()
logger = logging.getLogger(__name__)

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = None
    access_token: str = None

    @validator('refresh_token', 'access_token', pre=True, always=True)
    def check_token(cls, v, values, field):
        if not v and not any(values.get(k) for k in ['refresh_token', 'access_token']):
            raise ValueError("Either refresh_token or access_token must be provided")
        return v


@auth_router.post("/login", response_model=LoginResponse)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_repo: UserRepository = Depends(get_user_repository)
):
    user = await user_repo.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@auth_router.post("/refresh", response_model=Token)
async def refresh_access_token(token_data: RefreshTokenRequest):
    try:
        refresh_token = token_data.refresh_token
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is required"
            )

        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # access_token = create_access_token(
    #     data={"sub": email},
    #     expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    # )

    refresh_token = create_refresh_token(
        data={"sub": email}
    )

    return {
        # "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_repo: UserRepository = Depends(get_user_repository)
):
    email = decode_access_token(token)
    if email is None:
        logger.warning("Invalid token used for authentication")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user = await user_repo.get_by_email(email)
    if user is None:
        logger.warning(f"User not found for token: {token}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
