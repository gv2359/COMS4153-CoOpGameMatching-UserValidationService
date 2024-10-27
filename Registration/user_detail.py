from abc import ABC, abstractmethod
from typing import Any
from schemas import UserDetail
import uuid
from data_access import MySQLDataService
import os

class UserDetail(ABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserDetail, cls).__new__(cls)
        return cls._instance

    def __init__(self, config):
        self.config = config
        self.database = "UserProfile"
        self.collection = "user_info"
        self.key_field="email" #subject to change
        self.createDBService()

    def createDBService(self):
        db_context = {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "port": int(os.getenv("DB_PORT", 3306))  # Default to 3306 if not specified
        }
        self.data_service = MySQLDataService(db_context)

    def register(self, user: UserDetail) -> bool:
        user_data = {
            "userId": str(uuid.uuid4()),  # Generate a new UUID
            "password": user.password,
            "email": user.email,
            "displayName": user.displayName,
            "steamID": user.steamID
        }
        return self.data_service.insert_data_object("UserProfile", "user_info", user_data)
    
    def checkUserExists(self, email: str) -> bool:
        existing_user = self.data_service.get_data_object("UserProfile", "user_info", "email", email)
        return existing_user

        
