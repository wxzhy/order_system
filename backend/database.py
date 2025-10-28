from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from sqlmodel import create_engine
from fastapi import FastAPI
import urllib.parse

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
mysql_url = (
    f"mysql+mysqldb://{DB_USER}:{escaped_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# (可选) 打印出来看看转义后的效果
# 它会打印出: mysql+mysqldb://order:1Qaz%402wsx%21%23@localhost:3306/ordersystem
print(f"构建的URL: {mysql_url}")

engine = None


async def get_engine():
    if engine is None:
        raise Exception("数据库引擎未初始化")
    return engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    engine = create_engine(mysql_url, echo=True)
    if engine is None:
        raise Exception("无法创建数据库引擎")
    SQLModel.metadata.create_all(engine)
    yield
    engine.dispose()
