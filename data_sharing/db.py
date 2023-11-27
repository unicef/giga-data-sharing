from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from data_sharing.settings import settings

engine = create_async_engine(settings.ASYNC_DATABASE_URL)

session = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)


async def get_db():
    db = session()
    try:
        yield db
    finally:
        await db.close()
