"""
初始化脚本 - 创建默认管理员账户
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import select
from backend.database import get_engine
from backend.models import User, UserType
from backend.security import get_password_hash


async def create_default_admin():
    """创建默认管理员账户"""
    engine = await get_engine()
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # 检查是否已存在管理员
        statement = select(User).where(User.user_type == UserType.ADMIN)
        existing_admin = (await session.execute(statement)).scalars().first()

        if existing_admin:
            print("管理员账户已存在，无需创建")
            return

        # 创建默认管理员
        admin = User(
            username="admin",
            email="admin@ordersystem.com",
            phone="10086",
            hashed_password=get_password_hash("admin123456"),
            user_type=UserType.ADMIN,
        )

        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        print("=" * 50)
        print("默认管理员账户创建成功！")
        print("=" * 50)
        print(f"用户名: {admin.username}")
        print(f"邮箱: {admin.email}")
        print("密码: admin123456")
        print(f"用户ID: {admin.id}")
        print("=" * 50)
        print("⚠️  请立即修改默认密码！")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(create_default_admin())
