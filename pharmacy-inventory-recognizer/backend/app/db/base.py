"""SQLAlchemy declarative base shared by every model."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
