from django.urls import path
from .views import TaskCreateView, TaskUpdateView, TaskDeleteView

urlpatterns = [
    path('create/', TaskCreateView.as_view(), name='task'),
    path('/<int:pk>/update', TaskUpdateView.as_view(), name='task_update'),
    path('/<int:pk>/delete', TaskDeleteView.as_view(), name='task_delete'),
]