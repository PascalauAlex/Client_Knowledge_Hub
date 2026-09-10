from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from typing import Annotated
from config import settings
from pgvector.psycopg import register_vector_async



engine = create_async_engine(
    url=settings.database_url,
    echo=True,
)
from sqlalchemy import event

@event.listens_for(engine.sync_engine, "connect")
def connect(dbapi_connection, connection_record):
    dbapi_connection.run_async(register_vector_async)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)





async def get_db():
    async with AsyncSessionLocal() as session:
        yield session



DbSession = Annotated[AsyncSession,Depends(get_db)] 