from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, String, UniqueConstraint, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import bcrypt
import uuid
import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error

load_dotenv()

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dbuserdbuser")
DB_NAME = os.getenv("DB_NAME", "user")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class UserInfo(Base):
    __tablename__ = 'user_info'
    __table_args__ = (UniqueConstraint('emailId', name='uq_email'),)

    userId = Column(String(36), primary_key=True, default=str(uuid.uuid4()))  # Specify length
    userName = Column(String(50), nullable=False)  # Specify length
    emailId = Column(String(100), unique=True, nullable=False)  # Specify length
    hashedPassword = Column(String(128), nullable=False)  # Specify length
    accessToken = Column(String(256), nullable=True)  # Specify length

# Function to create database if it doesn't exist
def create_database_if_not_exists():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error creating database: {e}")

# Create tables at startup if they don't exist
def create_tables():
    Base.metadata.create_all(bind=engine)

# Initialize the database and create tables
create_database_if_not_exists()
create_tables()

app = FastAPI()

class UserRegister(BaseModel):
    userName: str
    emailId: EmailStr
    password: str

class UserLogin(BaseModel):
    emailId: EmailStr
    password: str

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register")
async def register(user: UserRegister):
    db: Session = SessionLocal()
    existing_user = db.query(UserInfo).filter(UserInfo.emailId == user.emailId).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = UserInfo(
        userName=user.userName,
        emailId=user.emailId,
        hashedPassword=hashed_password.decode('utf-8'),
        accessToken=None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(user: UserLogin):
    db: Session = SessionLocal()
    existing_user = db.query(UserInfo).filter(UserInfo.emailId == user.emailId).first()
    if not existing_user or not bcrypt.checkpw(user.password.encode('utf-8'), existing_user.hashedPassword.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create access token with expiration
    access_token = create_access_token(data={"sub": existing_user.userId})
    existing_user.accessToken = access_token
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
async def logout(authorization: str = Header(...)):
    # Extract the token from the header
    token = authorization.split(" ")[1]  # Bearer <token>

    try:
        # Decode the token to get user ID
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")  # Extract user ID from the payload

        db: Session = SessionLocal()
        existing_user = db.query(UserInfo).filter(UserInfo.userId == user_id).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Invalidate the access token
        existing_user.accessToken = None
        db.commit()
        return {"message": "Successfully logged out"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/validate-token")
async def validate_token(authorization: str = Header(...)):
    # Extract token from the Authorization header
    token = authorization.split(" ")[1]  # Bearer <token>
    
    try:
        # Decode the token to get user ID
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")  # Extract user ID from the payload

        # Check if the user and token are valid in the database
        db: Session = SessionLocal()
        user = db.query(UserInfo).filter(UserInfo.userId == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.accessToken != token:
            raise HTTPException(status_code=401, detail="Token is invalid or expired")

        # If valid, return the user ID
        return {"user_id": user.userId}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/health")
async def health_check():
    return {"status": "UserValidationService is running"}
