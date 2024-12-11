from abc import ABC, abstractmethod

# TODO -- Implement the framework.
#


class BaseServiceFactory(ABC):

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def get_service(cls, service_name):
        raise NotImplementedError()