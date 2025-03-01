from fastapi import APIRouter



info_router = APIRouter()


@info_router.get("/")
async def get_hi():
    return {"message":"hello"}