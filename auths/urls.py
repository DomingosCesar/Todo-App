from django.urls import path
from . import views


urlpatterns = [
    # Authentication routes
    path('login/', views.AuthLogin.as_view(), name='login'),
    path('register/', views.AuthRegister.as_view(), name='register'),
    path('logout/', views.AuthLogoutView.as_view(), name='logout'),
    path('reset-password/', views.PassWordResetView.as_view(), name='reset-password-view'),
    path('reset-password/<int:id>/', views.PassWordReset.as_view(), name='reset-password'),
]
