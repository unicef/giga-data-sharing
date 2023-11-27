from contextlib import asynccontextmanager
from typing import AsyncContextManager

import sqlalchemy.exc
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from data_sharing.settings import settings

engine = create_engine(
    settings.DATABASE_URL, echo=not settings.IN_PRODUCTION, future=True
)

aengine = create_async_engine(
    settings.ASYNC_DATABASE_URL, echo=not settings.IN_PRODUCTION, future=True
)

session_maker = sessionmaker(bind=engine, autoflush=False, autocommit=False)

asession_maker = async_sessionmaker(
    bind=aengine, autoflush=False, autocommit=False, expire_on_commit=False
)


async def get_db():
    session = session_maker()
    try:
        yield session
    except sqlalchemy.exc.DatabaseError as e:
        logger.error(str(e))
        raise e
    finally:
        session.close()


async def get_async_db():
    session = asession_maker()
    try:
        yield session
    except sqlalchemy.exc.DatabaseError as e:
        logger.error(str(e))
        raise e
    finally:
        await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncContextManager[AsyncSession]:
    session = asession_maker()
    try:
        yield session
    except sqlalchemy.exc.DatabaseError as e:
        logger.error(str(e))
        raise e
    finally:
        await session.close()
