from fastapi import FastAPI, Request
import uvicorn
from starlette.responses import JSONResponse
import debugpy
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_admin.contrib.sqla import Admin, ModelView

from configs.db import engine, Base
from users.routes import user_router
from users.auth import auth_router
from users.models import Group, User, UserGroup
from sqlalchemy.future import select

debugpy.listen(("0.0.0.0", 5679))
print("✅ Debugpy is listening on port 5678. Waiting for debugger to attach...")

app = FastAPI()

app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(auth_router, prefix="/api", tags=["Auth"])

admin = Admin(engine, title="Admin Panel")
admin.add_view(ModelView(User))
admin.add_view(ModelView(UserGroup))
admin.add_view(ModelView(Group))
admin.mount_to(app)


async def seed_groups(db: AsyncSession):
    existing_groups = await db.execute(select(Group).where(Group.name.in_(["admin", "customer"])))
    existing_groups = {group.name for group in existing_groups.scalars().all()}

    new_groups = []
    if "admin" not in existing_groups:
        new_groups.append(Group(name="admin"))
    if "customer" not in existing_groups:
        new_groups.append(Group(name="customer"))

    if new_groups:
        db.add_all(new_groups)
        await db.commit()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        await seed_groups(session)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_detail = str(exc)
    error_trace = traceback.format_exc()
    print(f"Error: {error_detail}\n{error_trace}")
    return JSONResponse(
        status_code=500,
        content={"detail": error_detail}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
