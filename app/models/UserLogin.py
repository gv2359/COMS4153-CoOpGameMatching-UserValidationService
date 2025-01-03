from pydantic import BaseModel
from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()
class UserInfo(Base):
    __tablename__ = 'user_info'
    __table_args__ = (UniqueConstraint('email', name='uq_email'),)

    userId = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    userName = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    accessToken = Column(String(256), nullable=True)
    steamId = Column(String(100), nullable=True)
    role = Column(String(50), nullable=False)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class UserInfoResponse(BaseModel):
    user_id: str
    userName: str
    role: str

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
