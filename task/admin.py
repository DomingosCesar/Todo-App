from django.contrib import admin
from .models import Task, Category, Progress, Notification, Report


# Register your models here.

admin.site.register(Task)
admin.site.register(Category)
admin.site.register(Progress)
admin.site.register(Notification)
admin.site.register(Report)
