from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP
from sqlalchemy.orm import relationship
from db.base_class import Base
import enum


class UserType(enum.Enum):
    Admin = "Admin"
    InteractiveUser = "InteractiveUser"
    ExternalUser = "ExternalUser"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)

    courses = relationship("Course", back_populates="creator")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
