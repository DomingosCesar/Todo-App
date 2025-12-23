from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .utils import send_reset_password_email
from auths.services import UserService
from .forms import UserRegisterForm, UserLoginForm, PassWordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
# Create your views here.


class AuthRegister(View):
    form_class = UserRegisterForm
    model = UserService()
    name = 'register'
    template_name = "auth/auth_form.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'name':self.name, 'form': self.form_class})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            if form.cleaned_data['password'] == form.cleaned_data['confirm_password']:
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                username = email.split('@')[0]
                user = self.model.getRepository().create_user(username=str.capitalize(username), email=email, password=password)
                
                messages.success(request, 'Cadastro realizado com sucesso.')
                return redirect('login')
            else:
                messages.warning(request, 'Passwords diferentes')
        else:
            messages.warning(request, 'Por favor, corrija os erros abaixo.')
            return redirect('register')
    
class AuthLogin(View):
    form_class = UserLoginForm
    name = 'login'
    template_name = "auth/auth_form.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'name':self.name, 'form': self.form_class})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']
            # pass identifier (email or phone) to authentication backend
            user = authenticate(request, identifier=identifier, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login realizado com sucesso.')
                return redirect('index')
            else:
                messages.warning(request, 'Email ou senha inválidos.')
                return redirect('login')
        else:
            messages.warning(request, 'Por favor, corrija os erros abaixo.')
        return render(request, self.template_name, {'name':self.name, 'form':form})

class PassWordResetView(View):
    template_name = "auth/password_reset_view.html"
    service = UserService()
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        try:
            email = request.POST.get('email_reset')
            user = self.service.getRepository().getUserByEmail(email)
            if user:
                send_reset_password_email(user)
                messages.warning(request, 'Awesome, you will receive an email in your box. Click in button to reset your password!')
            else:
                messages.warning(request, 'Unfortunately this e-mail is not associated with your account!')
        except Exception as e:
            messages.warning(request, 'Unfortunately this e-mail is not associated with your account!')
        return render(request, self.template_name)
    
class PassWordReset(View):
    form_class = PassWordResetForm
    service = UserService()
    template_name = "auth/password_reset.html"
    
    def get(self, request, pk, *args, **kwargs):
        user = self.service.getRepository().getUserById(pk)
        return render(request, self.template_name, {'form': self.form_class(), 'user': user})
    
    def post(self, request, pk, *args, **kwargs):
        form = self.form_class(request.POST)
        user = self.service.getRepository().getUserById(pk)
        if form.is_valid():
            if request.POST.get('password') == request.POST.get('confirm_password'):
                new_password = str(request.POST.get('password'))
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Successful resetting Password!')
                return redirect('login')
            else:
                messages.warning(request, 'Passwords are different!')
        else:
            messages.warning(request, 'Fail Resetting password, because form is invalid!')
        return render(request, self.template_name, {'form': form, 'user': user})
    

class AuthLogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        request.session.delete()
        return redirect('login')