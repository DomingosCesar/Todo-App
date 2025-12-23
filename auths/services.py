from .repository import UserRepository
from .models import User


class UserService:
    def __init__(self, repository=None):
        if repository is None:
            self.__repository = UserRepository(User)
        else:
            self.__repository = repository
        
    def getRepository(self): return self.__repository