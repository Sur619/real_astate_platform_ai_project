from fastapi import FastAPI, Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.templating import Jinja2Templates
import uvicorn
import debugpy

from configs.db import engine, Base
from users.routes import user_router
from users.auth import auth_router
from users.models import Group
from middleware.admin_panel import AdminAuthMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette_admin.contrib.sqla import Admin, ModelView
from configs.settings import Settings

app = FastAPI()
settings = Settings()

# Роутери
app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(auth_router, prefix="/api", tags=["Auth"])

# Адмінка
admin = Admin(engine, title="Admin Panel")
admin.add_view(ModelView(Group))
admin.mount_to(app)

# Middleware
app.add_middleware(AdminAuthMiddleware)


# 🧪 Seed початкових груп (admin, customer)
async def seed_groups(db: AsyncSession):
    existing = await db.execute(select(Group).where(Group.name.in_(["admin", "customer"])))
    existing_names = {group.name for group in existing.scalars().all()}

    new_groups = []
    if "admin" not in existing_names:
        new_groups.append(Group(name="admin"))
    if "customer" not in existing_names:
        new_groups.append(Group(name="customer"))

    if new_groups:
        db.add_all(new_groups)
        await db.commit()


# ⚙️ Створити таблиці та групи при запуску
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        await seed_groups(session)


# 🧨 Глобальний хендлер помилок
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_detail = str(exc)
    error_trace = traceback.format_exc()
    print(f"Error: {error_detail}\n{error_trace}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"} if not settings.debug else {"detail": error_detail}
    )


# 🌐 Шаблони
templates = Jinja2Templates(directory="templates")


# 📄 Сторінка логіну для адмінів
@app.get("/api/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


# 🚀 Запуск
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 👈 ОЦЕ головне для дебагу!
        log_level="debug"
    )
