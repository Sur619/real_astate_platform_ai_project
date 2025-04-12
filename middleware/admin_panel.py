from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse, JSONResponse
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from configs.db import engine
from users.models import User
from users.utils import is_admin
from users.auth import decode_access_token


class AdminAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"📡 Incoming request: {request.url.path}")
        # Перевіряємо, чи це /admin
        if request.url.path.startswith("/admin"):
            token = None

            # З cookie
            if "token" in request.cookies:
                token = request.cookies["token"]

            # З Authorization заголовку
            if not token and "Authorization" in request.headers:
                auth_header = request.headers["Authorization"]
                if auth_header.startswith("Bearer "):
                    token = auth_header.replace("Bearer ", "")

            # Якщо токена немає — редірект на логін
            if not token:
                return RedirectResponse(url="/api/login")

            try:
                email = decode_access_token(token)
                if not email:
                    return RedirectResponse(url="/api/login")

                async with AsyncSession(engine) as session:
                    stmt = select(User).options(selectinload(User.groups)).where(User.email == email)
                    result = await session.execute(stmt)
                    user = result.unique().scalar_one_or_none()

                    if not user:
                        return RedirectResponse(url="/api/login")

                    # Якщо не адмін — 403
                    if not is_admin(user):
                        return JSONResponse(
                            status_code=403,
                            content={"detail": "Access denied: Admin privileges required"}
                        )

            except Exception as e:
                import traceback
                print(f"Admin auth error: {str(e)}\n{traceback.format_exc()}")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid authentication credentials"}
                )

        # Якщо все добре або це не /admin — передаємо далі
        return await call_next(request)
