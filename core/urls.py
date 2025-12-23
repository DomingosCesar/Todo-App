from django.urls import path
from . import views

urlpatterns = [
    path('', views.Core.as_view(), name='index'),
]
