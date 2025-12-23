from django.urls import path
from .views import TaskCreateView, TaskUpdateView, TaskDeleteView, ProgressUpdateView, CompleteTaskDailyView

urlpatterns = [
    path('create/', TaskCreateView.as_view(), name='task'),
    path('<int:pk>/update', TaskUpdateView.as_view(), name='task_update'),
    path('<int:pk>/delete', TaskDeleteView.as_view(), name='task_delete'),
    path('progress/<int:id>/', ProgressUpdateView.as_view(), name='progress'),
    path('<int:task_id>/daily_complete/', CompleteTaskDailyView.as_view(), name='completar_diariamente'),
]