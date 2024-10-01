# main.py
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import uuid
import os
from data_access import MySQLDataService
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# MySQL connection settings
db_context = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", 3306))  # Default to 3306 if not specified
}

data_service = MySQLDataService(db_context)

# User model
class User(BaseModel):
    userId: Optional[str] = None
    password: str
    email: str
    displayName: str
    steamID: str


@app.post("/register")
def register_user(user: User):
    # Check if user already exists
    existing_user = data_service.get_data_object("UserProfile", "user_info", "email", user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Prepare user data for insertion
    user_data = {
        "userId": str(uuid.uuid4()),  # Generate a new UUID
        "password": user.password,
        "email": user.email,
        "displayName": user.displayName,
        "steamID": user.steamID
    }

    # Insert user into database
    success = data_service.insert_data_object("UserProfile", "user_info", user_data)
    if not success:
        raise HTTPException(status_code=500, detail="Error registering user")

    return {"message": "User registered successfully!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)