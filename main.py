from fastapi import FastAPI
import uvicorn
from fastapi.routing import APIRouter
from api.handlers import info_router
app = FastAPI()
main_api_router = APIRouter()



main_api_router.include_router(info_router, prefix="/info_router", tags=["info_router"])
app.include_router(main_api_router)


if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(app, host="0.0.0.0", port=8000)
    