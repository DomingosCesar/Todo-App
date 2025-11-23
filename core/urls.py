from django.urls import path
from . import views

urlpatterns = [
    path('', views.Core.index, name='index'),
    # Authentication routes
    path('auth/login/', views.Auth.login, name='login'),
    path('auth/register/', views.Auth.register, name='register'),
    path('auth/register/store', views.Auth.store, name='store'),
]
