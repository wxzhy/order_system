from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi import FastAPI
import urllib.parse

from .config import get_config

# 从配置文件读取数据库配置
config = get_config()
db_config = config["database"]

DB_USER = db_config["user"]
DB_PASS = db_config["password"]
DB_HOST = db_config["host"]
DB_PORT = db_config["port"]
DB_NAME = db_config["name"]

# 仅对密码进行转义
escaped_password = urllib.parse.quote_plus(DB_PASS)

# 使用 f-string 安全地构建连接字符串
mysql_url = (
    f"mysql+asyncmy://{DB_USER}:{escaped_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f"构建的URL: {mysql_url}")

engine = None


async def get_engine():
    if engine is None:
        raise Exception("数据库引擎未初始化")
    return engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    engine = create_async_engine(mysql_url, echo=True, pool_pre_ping=True)
    if engine is None:
        raise Exception("无法创建数据库引擎")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    # SQLModel.metadata.create_all(engine.sync_engine)
    yield
    await engine.dispose()
