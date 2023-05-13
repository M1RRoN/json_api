from sqlalchemy import Column, Integer, String, Boolean

from database import Base


class UserInfo(Base):
    __tablename__ = "_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)


class ObjectInfo(Base):
    __tablename__ = '_object'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

