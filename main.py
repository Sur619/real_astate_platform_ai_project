from fastapi import FastAPI, Request
import uvicorn
from starlette.responses import JSONResponse

from users.routes import user_router
from sqlalchemy.ext.asyncio import AsyncSession
from configs.db import engine, Base

app = FastAPI()

app.include_router(user_router, prefix="/api", tags=["Users"])


@app.on_event("startup")
async def startup():
    # Создаем таблицы в базе данных при запуске
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Для отладки - выводит информацию о любых непойманных исключениях
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
