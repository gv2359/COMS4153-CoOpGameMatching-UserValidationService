from fastapi import FastAPI, HTTPException, Header
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import jwt
import os
import pymysql
from dotenv import load_dotenv
from datetime import datetime, timedelta
from models import UserInfo, LoginResponse, MessageResponse, ErrorResponse, Base, ValidateTokenResponse
from firebase_admin import auth, credentials, initialize_app
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Firebase Admin SDK Initialization
cred = credentials.Certificate(os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY"))
initialize_app(cred)

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

# # Create the database if it doesn't exist
# try:
#     with connection.cursor() as cursor:
#         cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
#     print(f"Database '{DB_NAME}' created successfully (if it didn't already exist).")
# finally:
#     connection.close()

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

# Need this for CORS otherwise the frontend won't be able to access the API locally, comment out for cloud
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

@app.post("/login-google", response_model=LoginResponse, responses={400: {"model": ErrorResponse}})
async def login_google(authorization: str = Header(...)):
    """
    Handle login using Firebase ID Token.
    """
    db = SessionLocal()
    id_token = authorization.split(" ")[1]  # Extract Firebase ID token
    try:
        # Verify Firebase ID Token
        decoded_token = auth.verify_id_token(id_token)
        # print(decoded_token)
        email = decoded_token["email"]
        name = decoded_token.get("name", "User")
        # Check if the user exists in the database
        user = db.query(UserInfo).filter(UserInfo.email == email).first()
        if not user:
            # Register a new user
            user = UserInfo(userName=name, email=email, accessToken=None, role="user")
            db.add(user)

        # Create custom JWT
        access_token = create_access_token({"sub": user.userId, "role": user.role})

        # Update existing user's access token
        user.accessToken = access_token

        db.commit()
        db.refresh(user)

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")

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
    except Exception as e:
        print(e)

@app.post("/validate-token", response_model=ValidateTokenResponse, responses={401: {"model": ErrorResponse}})
async def validate_token(authorization: str = Header(...)):
    token = authorization.split(" ")[1]  # Bearer <token>
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")

        db = SessionLocal()
        user = db.query(UserInfo).filter(UserInfo.userId == user_id).first()

        if not user or user.accessToken != token:
            raise HTTPException(status_code=401, detail="Token is invalid or expired")

          # If valid, return the user ID and user name
        return {"user_id": user.userId, "userName": user.userName, "role": user.role}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/health", response_model=MessageResponse)
async def health_check():
    return {"message": "UserValidationService is running"}
