from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Modelo User herda de AbstractUser para incluir campos como username, se desejar;
    # Senao, use model.Model
    
    """_Model for users of app Todo List.
    Note: if does not want to use authentication built-in of django, changing for models.Model and add username as CharField.
    """
    # name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=150, unique=True, null=False, blank=False)
    password_hash = models.CharField(max_length=255, null=False, blank=False) # Armazene has da senha (use make_password no forms)
    date_create = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        # db_table = 'user' # Name of table on database
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return self.username
    
    
class Profile(models.Model):
    """
        Profile extended of user (relationship 1:1)
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profiles')
    avatar_url = models.URLField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(verbose_name='numero telefonico', max_length=255, null=True, blank=True)
    birth_date = models.DateField(verbose_name='data de nascimento', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    preference = models.JSONField(default=dict) # Ex: {"tema":"dark", "idioma":"pt"} 
    
    class Meta:
        # db_table = 'profile'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        
    def __str__(self):
        return f'Profile of {self.user.name}'