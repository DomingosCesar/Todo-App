from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators import csrf
from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework import serializers
from django.contrib import messages
from django.views import View
from .forms import TaskForm
from .models import Task, DailyRegister
from task.services import TaskService
from datetime import date
import json

class TaskCreateView(LoginRequiredMixin, View):
    """
        View para criação de tarefas, contendo o metodo get e post
    """
    form_class = TaskForm
    initial = {"key": "value"}
    template_name = "tasks/create_form.html"
    model = TaskService()
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form":form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            self.model.getRepository().create_task(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                category=form.cleaned_data["category"],
                date_expired=form.cleaned_data["date_expired"],
                priority=form.cleaned_data["priority"],
                status=form.cleaned_data["status"],
                user=request.user
            )
            messages.success(request, "✨ Tarefa criada com sucesso!")
            # Redirecionar para a página anterior (referrer) ou para index
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            messages.warning(request, '❌ Tarefa não foi criada. Corrija os erros.')
        return render(request, self.template_name, {"form":form})
    
class TaskUpdateView(LoginRequiredMixin, View):
    form_class = TaskForm
    initial = {"key": "value"}
    model = TaskService()
    user = get_user_model()
    template_name = 'tasks/update_form.html'
    
    # @login_required(login_url='login')
    def get(self, request, pk, *args, **kwargs):
        form = self.form_class(initial=self.initial, instance=self.model.getRepository().getTaskById(id=pk))
        return render(request, self.template_name, {"form":form})
    
    # @login_required(login_url='login')
    def post(self, request, pk, *args, **kwargs):
        form = form = self.form_class(request.POST, instance=self.model.getRepository().getTaskById(id=pk))
        if form.is_valid():
            form.save()
            messages.success(request, "Task editado com sucesso!")
            return redirect("index")
        else:
            print("Falha ao atualizar a tarefa!")
            messages.warning(request, "Falha ao atualizar a tarefa!")
        return render(request, self.template_name, {"form":form})
    
class TaskDeleteView(LoginRequiredMixin, View):
    model = TaskService()
    template_name = 'tasks/delete_form.html'
    
    def get(self, request, pk, *args, **kwargs):
        task = self.model.getRepository().getTaskById(id=pk)
        return render(request, self.template_name, {"task":task})
    
    def post(self, request, pk, *args, **kwargs):
        message = self.model.getRepository().deleteTaskById(id=pk)
        if message: messages.info(request, message)
        else: messages.error(request, "Error, Task with this id not exist!")
        return redirect("index")
    
class ProgressUpdateView(View):
    @csrf_exempt
    def get(self, request, id, *args, **kwargs):
        task = Task.objects.get(id=id)
        # task.update_progress_points()
        print(task.progress_points)
        return JsonResponse(data={"data":task.progress_points}, status=200)

class ProgressView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pass

class CompleteTaskDailyView(LoginRequiredMixin, View):
    def get(self, request, task_id, *args, **kwargs):
        return redirect("index")
    
    def post(self, request, task_id, *args, **kwargs):
        user = request.user
        
        # 1. Filtro de seguranca, garante que a tarefa pertence a um usuario
        task = get_object_or_404(task, id=task_id)
        
        today_date = date.today()
        
        # 2. Impedir conclusao se o prazo final ja passou
        if task.expired_date and today_date > task.expired_date:
            # Tarefa expirada
            return redirect("index")
        
        # 3. Tentativa de registro diario
        try:
            DailyRegister.objects.create(
                task=task,
                completed_per=request.user
            )
            
            # Opcional: Se hoje e o ultimo dia, marcamos a tarefa comc finalizada.
            if task.expired_date == today_date:
                task.concluded = True
                task.save()
                
        except IntegrityError:
            # Erro: Já existe um RegistroDiario para esta tarefa e para a data de hoje.
            # O usuário tentou clicar no botão duas vezes no mesmo dia.
            pass # Ignoramos silenciosamente ou exibimos uma mensagem flash
        return redirect("index")
        