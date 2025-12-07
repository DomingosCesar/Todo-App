from django.urls import path
from . import views

urlpatterns = [
    path('', views.Core.as_view(), name='index'),
    # Authentication routes
    path('auth/login/', views.AuthLogin.as_view(), name='login'),
    path('auth/register/', views.AuthRegister.as_view(), name='register'),
    path('auth/logout/', views.AuthLogoutView.as_view(), name='logout'),
    path('auth/reset-password/', views.PassWordResetView.as_view(), name='reset-password-view'),
    path('auth/reset-password/<int:id>/', views.PassWordReset.as_view(), name='reset-password'),
]
