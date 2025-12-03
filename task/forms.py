from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'date_expired', 'priority', 'status']
        
        widgets = {
            'date_expired': forms.DateInput(attrs={"type":"date"})
        }