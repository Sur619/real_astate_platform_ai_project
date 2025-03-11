from datetime import timedelta
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from users.repositories import UserRepository, get_user_repository
from users.schema import Token
from users.security import verify_password, create_access_token, decode_access_token
from configs.settings import Settings

auth_router = APIRouter()
logger = logging.getLogger(__name__)

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@auth_router.post("/login", response_model=Token)
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
    return {"access_token": access_token, "token_type": "bearer"}


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
