from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views import View
from .forms import TaskForm
from .models import Task



class TaskCreateView(LoginRequiredMixin, View):
    """
        View para criação de tarefas, contendo o metodo get e post
    """
    form_class = TaskForm
    initial = {"key": "value"}
    template_name = "tasks/create_form.html"
    model = Task
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form":form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            self.model.objects.create(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                category=form.cleaned_data["category"],
                date_expired=form.cleaned_data["date_expired"],
                priority=form.cleaned_data["priority"],
                status=form.cleaned_data["status"],
                user=request.user
            )
            print("Tarefa criada com sucesso.")
            messages.success(request, "Tarefa criada com sucesso.")
            return redirect('index')
        else:
            print('Tarefa nao foi criada')
            messages.warning(request, 'Tarefa nao foi criada')
        return render(request, self.template_name, {"form":form})
    
class TaskUpdateView(LoginRequiredMixin, View):
    form_class = TaskForm
    initial = {"key": "value"}
    model = Task
    user = get_user_model()
    template_name = 'tasks/update_form.html'
    
    # @login_required(login_url='login')
    def get(self, request, pk, *args, **kwargs):
        form = self.form_class(initial=self.initial, instance=Task.objects.get(id=pk))
        return render(request, self.template_name, {"form":form})
    
    # @login_required(login_url='login')
    def post(self, request, pk, *args, **kwargs):
        form = form = self.form_class(request.POST, instance=Task.objects.get(id=pk))
        if form.is_valid():
            form.save()
            messages.success(request, "Task editado com sucesso!")
            return redirect("index")
        else:
            print("Falha ao atualizar a tarefa!")
            messages.warning(request, "Falha ao atualizar a tarefa!")
        return render(request, self.template_name, {"form":form})
    
class TaskDeleteView(LoginRequiredMixin, View):
    model = Task
    template_name = 'tasks/delete_form.html'
    
    def get(self, request, pk, *args, **kwargs):
        task = self.model.objects.get(id=pk)
        return render(request, self.template_name, {"task":task})
    
    def post(self, request, pk, *args, **kwargs):
        task = self.model.objects.get(id=pk)
        task.delete()
        messages.info(request, "Task Deletada com sucesso!")
        
        return redirect("index")
    
