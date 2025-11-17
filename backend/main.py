from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback

from backend.database import lifespan
from backend.routers import auth, user, store, item, order, comment, stats

app = FastAPI(
    title="食堂餐点预定系统",
    description="食堂餐点预定系统接口",
    version="1.0.0",
    lifespan=lifespan,
)


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """捕获所有未处理的异常并返回详细错误信息"""
    error_detail = {
        "error": str(exc),
        "type": type(exc).__name__,
        "traceback": traceback.format_exc(),
    }
    print(f"\n{'=' * 50}")
    print(f"ERROR in {request.method} {request.url}")
    print(f"Exception: {type(exc).__name__}: {exc}")
    print(f"Traceback:\n{traceback.format_exc()}")
    print(f"{'=' * 50}\n")
    return JSONResponse(status_code=500, content=error_detail)


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
