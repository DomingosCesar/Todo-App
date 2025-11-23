from django.shortcuts import render, redirect
from django.core.paginator import Paginator


class Core:
    def index(request):
        return render(request, 'index.html')

class Auth:
    def register(request):
        name = 'register'
        return render(request, 'auth/auth_form.html', {'name':name})
    
    def store(request):
        return redirect('index')
    
    def login(request):
        name = 'login'
        return render(request, 'auth/auth_form.html', {'name':name})
