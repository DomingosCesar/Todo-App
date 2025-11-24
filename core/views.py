from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserRegisterForm, UserLoginForm

User = get_user_model()
class Core:
    def index(request):
        return render(request, 'index.html')

class Auth:
    def register(request):
        name = 'register'
        form = UserRegisterForm()
        return render(request, 'auth/auth_form.html', {'name':name, 'form': form})
    
    def store(request):
        form = UserRegisterForm()
        print(form)
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                if form.cleaned_data['password'] == form.cleaned_data['confirm_password']:
                    email = form.cleaned_data['email']
                    password = form.cleaned_data['password']
                    username = email.split('@')[0]
                    user = User.objects.create_user(str.capitalize(username), email, password)
                    print('Usuario cadastrado com sucesso!')
                    messages.success(request, 'Cadastro realizado com sucesso.')
                    return redirect('login')
                else:
                    messages.warning(request, 'Passwords diferentes')
                    print('Passwords diferentes')
            
            else:
                messages.warning(request, 'Por favor, corrija os erros abaixo.')
                return redirect('register')
    
    def login(request):
        name = 'login'
        return render(request, 'auth/auth_form.html', {'name':name})
