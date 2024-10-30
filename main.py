from fastapi import FastAPI, HTTPException, Header
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt
import jwt
import os
import pymysql
from dotenv import load_dotenv
from datetime import datetime, timedelta
from models import UserInfo, UserRegister, UserLogin, LoginResponse, MessageResponse, ErrorResponse, Base, ValidateTokenResponse

load_dotenv()

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dbuserdbuser")
DB_NAME = os.getenv("DB_NAME", "user")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# First, connect without specifying a database
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    port=int(DB_PORT),
    autocommit=True
)

# Create the database if it doesn't exist
try:
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    print(f"Database '{DB_NAME}' created successfully (if it didn't already exist).")
finally:
    connection.close()

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables at startup if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register", response_model=MessageResponse, responses={400: {"model": ErrorResponse}})
async def register(user: UserRegister):
    db = SessionLocal()
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

@app.post("/login", response_model=LoginResponse, responses={400: {"model": ErrorResponse}})
async def login(user: UserLogin):
    db = SessionLocal()
    existing_user = db.query(UserInfo).filter(UserInfo.emailId == user.emailId).first()
    if not existing_user or not bcrypt.checkpw(user.password.encode('utf-8'), existing_user.hashedPassword.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": existing_user.userId})
    existing_user.accessToken = access_token
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout", response_model=MessageResponse, responses={401: {"model": ErrorResponse}})
async def logout(authorization: str = Header(...)):
    token = authorization.split(" ")[1]  # Bearer <token>
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        db = SessionLocal()
        existing_user = db.query(UserInfo).filter(UserInfo.userId == user_id).first()
        if not existing_user or existing_user.accessToken != token:
            raise HTTPException(status_code=404, detail="Token is invalid or expired")

        existing_user.accessToken = None
        db.commit()
        return {"message": "Successfully logged out"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/validate-token", response_model=ValidateTokenResponse, responses={401: {"model": ErrorResponse}})
async def validate_token(authorization: str = Header(...)):
    token = authorization.split(" ")[1]  # Bearer <token>
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        db = SessionLocal()
        user = db.query(UserInfo).filter(UserInfo.userId == user_id).first()

        if not user or user.accessToken != token:
            raise HTTPException(status_code=401, detail="Token is invalid or expired")

          # If valid, return the user ID and user name
        return {"user_id": user.userId, "userName": user.userName}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/health", response_model=MessageResponse)
async def health_check():
    return {"message": "UserValidationService is running"}
