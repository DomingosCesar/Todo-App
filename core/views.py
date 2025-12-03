from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .utils import send_reset_password_email
from django.contrib.auth import get_user_model
from .forms import UserRegisterForm, UserLoginForm, PassWordResetForm
from task.models import Task

User = get_user_model()

class Core(LoginRequiredMixin, View):
    model = Task
    template_name = "index.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            "tasks": self.model.objects.filter(user=request.user)})

class AuthRegister(View):
    form_class = UserRegisterForm
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
                user = User.objects.create_user(str.capitalize(username), email, password)
                
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
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        try:
            email = request.POST.get('email_reset')
            user = get_object_or_404(User, email=email)
            send_reset_password_email(user)
            messages.warning(request, 'Awesome, you will receive an email in your box. Click in button to reset your password!')
        except:
            messages.warning(request, 'Unfortunately this e-mail is not associated with your account!')
        return render(request, self.template_name)
    
class PassWordReset(View):
    form_class = PassWordResetForm
    model = User
    template_name = "auth/password_reset.html"
    
    def get(self, request, pk, *args, **kwargs):
        return render(request, self.template_name,{'form':self.form_class(), 'user':self.model.objects.get(id=pk)})
    
    def post(self, request, pk, *args, **kwargs):
        form = self.form_class(request.POST)
        user = self.model.get(id=pk)
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
        return render(request, '', {'form':form, 'user':user})
    

class AuthLogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        request.session.delete()
        return redirect('login')
