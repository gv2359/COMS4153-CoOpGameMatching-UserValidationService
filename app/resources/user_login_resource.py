from typing import Any
import os
import jwt

from framework.exceptions.user_token_exceptions import TokenExpiredException, TokenNotValidException
from framework.resources.base_resource import BaseResource
import uuid
from app.models.UserLogin import LoginResponse, MessageResponse, UserInfoResponse
from firebase_admin import auth, credentials, initialize_app
from datetime import datetime, timedelta

from app.services.service_factory import ServiceFactory



class UserLoginResource(BaseResource):

    def __init__(self, config):
        super().__init__(config)

        # TODO -- Replace with dependency injection.
        #
        self.data_service = ServiceFactory.get_service("UserLoginResourceDataService")

        self.database = "UserProfile"

        self.data_service.initialize(self.database)

        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

        # Firebase Admin SDK Initialization
        cred = credentials.Certificate(os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY"))
        initialize_app(cred)


    def login(self, id_token):

        decoded_token = auth.verify_id_token(id_token)

        email = decoded_token["email"]
        name = decoded_token.get("name", "User")
        role = "user"
        user_id = str(uuid.uuid4())

        access_token = self.create_access_token({"sub":user_id,"role":id_token})
        user = self.data_service.create_user(email, name, user_id, access_token)

        if not user:
            raise Exception("User not found")

        login_response = LoginResponse(access_token=access_token, token_type="bearer")
        return login_response

    def logout(self, access_token):
        try:
            payload = jwt.decode(access_token, self.JWT_SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id = payload.get("sub")

            user = self.data_service.get_user(user_id)

            if not user or user.accessToken != access_token:
                raise Exception("Token not valid")

            self.data_service.invalidate_user(user_id)

            message_response = MessageResponse(message="User successfully logged out")
            return message_response

        except jwt.ExpiredSignatureError:
            raise TokenExpiredException(message="Token has expired")
        except jwt.InvalidTokenError:
            raise TokenNotValidException(message="Invalid token")

    def validate_token(self, access_token):
        try:
            payload = jwt.decode(access_token, self.JWT_SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id = payload.get("sub")
            role = payload.get("role")

            user = self.data_service.get_user(user_id)

            if not user or user.accessToken != access_token:
                raise Exception("Token not valid")

            user_info = UserInfoResponse(user_id=user.userId, userName= user.userName, role=user.role)
            return user_info

        except jwt.ExpiredSignatureError:
            raise TokenExpiredException(message="Token has expired")
        except jwt.InvalidTokenError:
            raise TokenNotValidException(message="Invalid token")


    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta if expires_delta else timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.JWT_SECRET_KEY, algorithm=self.ALGORITHM)


