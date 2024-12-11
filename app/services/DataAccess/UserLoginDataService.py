
from framework.services.DataAccess.MySQLDataService import MySQLDataService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.UserLogin import UserInfo
from typing import Optional


class UserLoginDataService(MySQLDataService):

    def __init__(self, context):
        super().__init__(context)

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

    def create_user(self, user_name, email, user_id, access_token):
        session = self.get_session()
        query = session.query(UserInfo)

        user = query.filter(UserInfo.email == email).first()
        if not user:
            # Register a new user
            user = UserInfo(userName=user_name, email=email, userId=user_id, accessToken=None, role="user")
            session.add(user)

        user.accessToken = access_token

        session.commit()
        session.refresh(user)
        return user


    def get_user(self, user_id):
        session = self.get_session()
        query = session.query(UserInfo)

        user = query.filter(UserInfo.userId == user_id).first()

        return user

    def invalidate_user(self, user_id):
        session = self.get_session()
        query = session.query(UserInfo)

        existing_user = query.filter(UserInfo.userId == user_id).first()
        existing_user.accessToken = None

        session.commit()