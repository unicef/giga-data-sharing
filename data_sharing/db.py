from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data_sharing.settings import settings

engine = create_engine(settings.DATABASE_URL)

session = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session():
    return session()
