from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import lifespan
from backend.routers import auth, user, store, item, order, comment, stats

app = FastAPI(
    title="食堂餐点预定系统",
    description="食堂餐点预定系统接口",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(store.router)
app.include_router(item.router)
app.include_router(order.router)
app.include_router(comment.router)
app.include_router(stats.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Canteen Meal Reservation System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
