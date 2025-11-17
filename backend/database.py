from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi import FastAPI
import urllib.parse

<<<<<<< HEAD
# 2. 将连接信息拆分
DB_USER = "root"
DB_PASS = "1Qaz@wsx"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "ordersystem"

# 3. 仅对密码进行转义
#    (如果用户名也有特殊字符，也用同样的方法转义 DB_USER)
escaped_password = urllib.parse.quote_plus(DB_PASS)

# 4. 使用 f-string 安全地构建连接字符串
=======
from backend.config import get_config

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
>>>>>>> HEAD@{1}
mysql_url = (
    f"mysql+asyncmy://{DB_USER}:{escaped_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

<<<<<<< HEAD
# (可选) 打印出来看看转义后的效果
=======
>>>>>>> HEAD@{1}
print(f"构建的URL: {mysql_url}")

engine = None


async def get_engine():
    if engine is None:
        raise Exception("数据库引擎未初始化")
    return engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
<<<<<<< HEAD
    engine = create_async_engine(mysql_url, echo=True,pool_pre_ping=True)
=======
    engine = create_async_engine(mysql_url, echo=True, pool_pre_ping=True)
>>>>>>> HEAD@{1}
    if engine is None:
        raise Exception("无法创建数据库引擎")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    # SQLModel.metadata.create_all(engine.sync_engine)
    yield
    await engine.dispose()
