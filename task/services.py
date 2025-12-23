from .repository import TaskRepository
from .models import Task


class TaskService:
    def __init__(self, repository=None):
        if repository is None:
            self.__repository = TaskRepository(Task)
        else:
            self.__repository = repository
            
    def getRepository(self): return self.__repository