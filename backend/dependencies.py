from backend.database import get_engine
from sqlmodel import Session


async def get_session():
    engine = await get_engine()
    with Session(engine) as session:
        yield session
