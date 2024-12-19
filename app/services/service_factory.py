import os
from framework.services.service_factory import BaseServiceFactory
import app.resources.user_login_resource as user_login_resource
from app.services.DataAccess.UserLoginDataService import UserLoginDataService


class ServiceFactory(BaseServiceFactory):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_service(cls, service_name):

        context = {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT")),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
        }

        if service_name == 'UserLoginResource':
            result = user_login_resource.UserLoginResource(config=None)
        elif service_name == 'UserLoginResourceDataService':
            data_service = UserLoginDataService(context=context)
            result = data_service
        else:
            result = None

        return result