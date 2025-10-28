from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import lifespan

app = FastAPI(
    title="食堂餐点预定系统",
    description="食堂餐点预定系统接口",
    version="1.0.0",
    lifespan=lifespan,
)
# 关闭CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Canteen Meal Reservation System API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
