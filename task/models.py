from django.db import models
from auths.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

# Escolhas para campos ENUM
PRIORITY_CHOICES = [
    ('BAIXA', 'Baixa'),
    ('MEDIA', 'Média'),
    ('ALTA', 'Alta'),
]

STATUS_CHOICES = [
    ('PENDENTE', 'Pendente'),
    ('EM_ANDAMENTO', 'Em Andamento'),
    ('CONCLUIDA', 'Concluída'),
    ('CANCELADA', 'Cancelada'),
]

NOTIFICATION_TYPE_CHOICES = [
    ('LEMBRETE', 'Lembrete'),
    ('ATUALIZACAO', 'Atualização'),
    ('CONCLUSAO', 'Conclusão'),
]


class Category(models.Model):
    """
        Categories of tasks (can be global or personal per user)
    """
    name = models.CharField(max_length=100, null=False, blank=False)
    color =  models.CharField(max_length=7, default='#000000') # Hex color for UI
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', null=True, blank=True) # Optional
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        indexes = [ # Indices for performance
            models.Index(fields=['name', 'user']),
        ]
    
    # def save(self, **kwargs):
    #     super().save(**kwargs)
    
    def __str__(self):
        return self.name
    

class Task(models.Model):
    """
        Main Tasks of App.
    """ 
    title = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category', null=True, blank=True)
    date_expired = models.DateField(null=True, blank=True)
    priority  = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIA')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='tasks', null=True, blank=True)
    progress_points = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    
    
    concluded = models.BooleanField(default=False)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'task'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        indexes = [ # indexes for performance
            models.Index(fields=['user', 'status']),
            models.Index(fields=['date_expired']),
        ]
        
    
    def __str__(self):
        return self.title
    
    # def divide_(self): return int((100 // self.day_expired))
    
    # def update_progress_points(self): self.progress_points += self.divide_()
    
    def get_progress_points(self): return self.progress_points
    
    def get_day_expired(self):
        if (self.date_expired.year == self.date_creation.year) and (self.date_expired.month > self.date_creation.month) and (self.date_expired.day > self.date_creation.day):
            self.day_expired = int(self.date_expired.day - self.date_creation.day)
        elif (self.date_expired.year == self.date_creation.year) and (self.date_expired.month == self.date_creation.month) and (self.date_expired.day > self.date_creation.day):
            self.progress_points = int(self.date_expired.day - self.date_creation.day)
        elif (self.date_expired.year > self.date_creation.year) and (self.date_expired.month < self.date_creation.month) and (self.date_expired.day < self.date_creation.day):
            self.progress_points = int(self.date_creation.day - self.date_expired.day)
    


class DailyRegister(models.Model):
    """
    Registra cada vez que um usuário marca a tarefa como 'feita' no dia.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    # Define a data atual automaticamente na criação.
    conclusion_date = models.DateField(auto_now_add=True) 
    completed_per = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        # A restrição de banco de dados mais importante: garante que a mesma Tarefa 
        # só pode ser marcada como 'feita' UMA VEZ por dia.
        unique_together = ('task', 'completed_per')

    def __str__(self):
        return f"Feito em {self.conclusion_date} por {self.completed_per.username}"

class Progress(models.Model):
    """
        Tracking the progress of each task (relationship 1:1)
    """
    
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='progress')
    percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    date_update = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'progress'
        verbose_name = 'Progress'
        verbose_name_plural = 'Progresses'
        
    def __str__(self):
        return f'Progress of {self.task.title}: {self.percentage}%'
    
    def updateProgress(self):
        """ A percentagem é atualizada conoforme o estado da tarefa avança, com base"""
        self.percentage = 0
    

class Notification(models.Model):
    """
        Notifications and lembretes for users
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message = models.TextField(null=False, blank=False)
    type = models.CharField(max_length=15, choices=NOTIFICATION_TYPE_CHOICES, default='LEMBRETE')
    read_done = models.BooleanField(default=False)
    date_send = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [ # indexes for performance
            models.Index(fields=['user', 'read_done']),
            models.Index(fields=['task'])
        ]
        
    
    def __str__(self):
        return f'{self.type}: {self.message[:50]}...'
    

class Report(models.Model):
    """
        Report generated at a time (ex: via Celery or Cron).
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report')
    initial_period = models.CharField(null=False, blank=False)
    end_period = models.CharField(null=False, blank=False)
    total_task = models.IntegerField(default=0)
    concluded_task = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) # Ex: 75.50%
    resume = models.JSONField(default=dict) # Ex: {'categories':[...], 'insights': '...'}
    date_generation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        indexes = [# Indexes for reports for user and period
            models.Index(fields=['user', 'initial_period', 'end_period']),
        ]
        
    def __str__(self):
        return f'Report of {self.user.name} ({self.initial_period} to {self.end_period})'
    
    
class Preference(models.Model):
    """
        Define the system preferences
    """
    # Preferências de UI
    theme = models.CharField(max_length=5, choices=[('dark', 'Dark'), ('light', 'Light')], default='dark')
    language = models.CharField(max_length=2, choices=[('pt', 'Português'), ('en', 'Inglês')], default='pt')
    
    def __str__(self): return f"Theme: {self.theme}, Language: {self.language}"