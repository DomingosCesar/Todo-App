from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
# from .utils import send_reset_password_email
# from django.contrib.auth import get_user_model

from task.models import Task, Category
from datetime import date

# User = get_user_model()

class Core(LoginRequiredMixin, View):
    model = Task
    template_name = "index.html"
    
    def get(self, request, *args, **kwargs):
        # Buscar tarefas do usuário logado
        tasks = self.model.objects.filter(user=request.user).order_by('-date_creation')
        # Buscar categorias do usuário
        categories = Category.objects.filter(user=request.user)
        
        return render(request, self.template_name, {
            "list_with_status": tasks,
            "categories": categories
        })

