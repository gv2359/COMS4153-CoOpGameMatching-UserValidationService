from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class UserInfo(Base):
    __tablename__ = 'user_info'
    __table_args__ = (UniqueConstraint('emailId', name='uq_email'),)

    userId = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    userName = Column(String(50), nullable=False)
    emailId = Column(String(100), unique=True, nullable=False)
    hashedPassword = Column(String(128), nullable=False)
    accessToken = Column(String(256), nullable=True)

class UserRegister(BaseModel):
    userName: str
    emailId: EmailStr
    password: str

class UserLogin(BaseModel):
    emailId: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class ValidateTokenResponse(BaseModel):
    user_id: str
    userName: str

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
