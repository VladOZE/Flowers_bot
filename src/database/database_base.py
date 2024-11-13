from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from src.config.database_config import settings


engine = create_engine(url=settings.DATABASE_URL, echo=True,
                       pool_size=5, max_overflow=10)


Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
