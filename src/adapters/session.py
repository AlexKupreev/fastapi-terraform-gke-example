from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
DEFAULT_SESSION_FACTORY = sessionmaker(autocommit=False, autoflush=False, bind=engine)
