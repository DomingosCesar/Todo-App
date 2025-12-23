from .models import User, Profile


class UserRepository:
    def __init__(self, model:User):
        self.__model = model
    
    def getModel(self): return self.__model
    
    def create_user(self, username:str, email:str, password:str):
        return self.__model.objects.create_user(username=username, email=email, password=password)
    
    def getUsers(self):
        return self.__model.objects.all()
    
    def getUserById(self, id:int):
        try:
            user = self.__model.objects.get(id=id)
            if user: return user
        except self.__model.DoesNotExist:
            print("Error, User with this Id not exist!")
            return None
        
    def getUserByName(self, name:str):
        try:
            user = self.__model.objects.get(username=name)
            if user: return user
        except self.__model.DoesNotExist:
            print("User with this username not exist!")
            return None
        
    def getUserByEmail(self, email:str):
        try:
            user = self.__model.objects.get(email=email)
            if user: return user
        except self.__model.DoesNotExist:
            print("User with this email not exist!")
            return None
        except self.__model.MultipleObjectsReturned:
            print("Multiple users with this email exist!")
            return None