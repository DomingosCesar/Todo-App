from .models import Task


class TaskRepository:
    def __init__(self, model:Task):
        self.__model = model
        
    def getModel(self): return self.__model
    
    def create_task(self, title, description, category, date_expired, priority, status, user):
        return self.__model.objects.create(
            title=title,
            description=description,
            category=category,
            date_expired=date_expired,
            priority=priority,
            status=status,
            user=user
        )
        
    def getTasks(self): return self.__model.objects.all()
    
    def getTaskFilter(self, user): return self.__model.objects.filter(user=user).order_by('-date_creation')
    
    def getTaskById(self, id:int):
        try:
            task = self.__model.objects.get(id=id)
            if task: return task
        except self.__model.DoesNotExist:
            print("Error, Task with this Id not exist!")
            return None
    def getTaskByTitle(self, title): return self.__model.objects.get(title=title)
    
    def updateTaskById(self, user, form):
        try:
            task = self.getTaskById(id=user.id)
            if task:
                task.update(
                    title=form.form.cleaned_data["title"],
                    description=form.cleaned_data["description"],
                    category=form.cleaned_data["category"],
                    priority=form.cleaned_data["priority"],
                    status=form.cleaned_data["status"],
                )
                # task.objects.update
        except self.__model.DoesNotExist:
            print("Error, Task with this Id not exist!")
            return None
    
    def deleteTaskById(self, id:int):
        try:
            task = self.__model.objects.get(id=id)
            if task: 
                task.delete()
                return "Task deleted with success!"
        except self.__model.DoesNotExist:
            print('Error, Task with this id not exist!')
            return None
        