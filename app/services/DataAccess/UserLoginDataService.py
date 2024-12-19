import uuid
from framework.services.DataAccess.MySQLDataService import MySQLDataService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.UserLogin import UserInfo
from typing import Optional
from datetime import datetime, timedelta
import jwt
import os


class UserLoginDataService(MySQLDataService):

    def __init__(self, context):
        super().__init__(context)
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    def initialize(self, database_name):
        """
        Creates the database and tables if they do not exist.
        """
        self.engine = create_engine(
            f"mysql+pymysql://{self.context['user']}:{self.context['password']}@"
            f"{self.context['host']}:{self.context['port']}/{database_name}",
            echo=True  #
        )
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def create_user(self, user_name, email, role):
        session = self.get_session()
        query = session.query(UserInfo)
        access_token = None
        user = query.filter(UserInfo.email == email).first()
        if user:
            access_token = self.create_access_token({"sub": user.userId, "role": role})
        if not user:
            # Register a new user
            user_id = str(uuid.uuid4())
            access_token = self.create_access_token({"sub": user_id, "role": role})
            print(f"inside not user {user_id}")
            user = UserInfo(userName=user_name, email=email, userId=user_id, accessToken=None, role="user")
            session.add(user)

        user.accessToken = access_token

        session.commit()
        session.refresh(user)
        return user


    def get_user(self, user_id):
        session = self.get_session()
        query = session.query(UserInfo)

        print(f"inside get user {user_id}")

        user = query.filter(UserInfo.userId == user_id).first()

        return user

    def invalidate_user(self, user_id):
        session = self.get_session()
        query = session.query(UserInfo)

        existing_user = query.filter(UserInfo.userId == user_id).first()
        existing_user.accessToken = None

        session.commit()

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta if expires_delta else timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.JWT_SECRET_KEY, algorithm=self.ALGORITHM)