from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models
# from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import send_reset_password_email
from django.contrib.auth import get_user_model
from .forms import UserRegisterForm, UserLoginForm, PassWordResetForm

User = get_user_model()

class Core:
    @login_required(login_url='login')
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
        form = UserLoginForm()
        if request.method == 'POST':
            form = UserLoginForm(request.POST)
            # if form.is_valid():
            #     authenticate()
            #     return redirect('index')
            # else:
            #     messages.info(request, '') 
            #     return redirect('login')
            if form.is_valid():
                identifier = form.cleaned_data['identifier']
                password = form.cleaned_data['password']
                # pass identifier (email or phone) to authentication backend
                user = authenticate(request, identifier=identifier, password=password)
                print("Ola....", user)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login realizado com sucesso.')
                return redirect('index')
            else:
                messages.warning(request, 'Email ou senha inválidos.')
                print('Email/phone ou senha inválidos')
                return redirect('login')
        else:
            # print(form)
            messages.warning(request, 'Por favor, corrija os erros abaixo.')
        # else:
        #     messages.warning(request, 'Por favor, corrija os erros abaixo.')
        #     return redirect('login')
        return render(request, 'auth/auth_form.html', {'name':name, 'form':form})
    
    def password_reset_view(request):
        if request.method == 'POST':
            try:
                print(request.POST.get('email_reset'))
                email = request.POST.get('email_reset')
                user = get_object_or_404(User, email=email)
                print(user)
                # send_reset_password_email(user)
                messages.warning(request, 'Awesome, you will receive an email in your box. Click in button to reset your password!')
            except:
                messages.warning(request, 'Unfortunately this e-mail is not associated with your account!')
                print('Nao existe!') 
            
        return render(request, 'auth/password_reset_view.html')
    
    def password_reset(request, id:int):
        form = PassWordResetForm()
        user = User.objects.get(id=id)
        if request.method == 'POST':
            form = PassWordResetForm(request.POST)
            print(form)
            if form.is_valid():
                if request.POST.get('password') == request.POST.get('confirm_password'):
                    # print(request.POST.get('password'))
                    new_password = str(request.POST.get('password'))
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Successful resetting Password!')
                    return redirect('login')
                else:
                    messages.warning(request, 'Passwords are different!')
            else:
                messages.warning(request, 'Fail Resetting password, because form is invalid!')
                
        return render(request, 'auth/password_reset.html', {'form':form, 'user':user})
    
    @login_required(login_url='login')
    def logout_view(request):
        logout(request)
        request.session.delete()
        return redirect('login')
