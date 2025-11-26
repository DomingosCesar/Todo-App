from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'is_active', 'last_login', 'date_joined']
    search_fields = ['email', 'username']
    readonly_fields = ['date_joined', 'last_login']
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class CustomProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ['user']
    search_fields = []
    readonly_fields = []
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Profile, CustomProfileAdmin)
admin.site.register(User, CustomUserAdmin)