from django.db.models.signals import post_save
from django.dispatch import receiver
from models import Task, Progress


@receiver(post_save, sender=Task)
def update_progress(sender, instance, **kwargs):
    if instance.status == 'CONCLUIDA':
        progress, created = Progress.objects.get_or_create(task=instance)
        progress.percentage = 100
        progress.save()
        
    elif instance.status == 'PENDENTE':
        progress, created = Progress.objects.get_or_create(task=instance)
        progress.percentage = 0
        progress.save()