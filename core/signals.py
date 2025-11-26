from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, Profile
from .utils import send_mail, send_welcome_email, send_profile_update_email

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        # Send welcome email when user is created
        # if instance.email:  # Only send if email is provided
        #     send_welcome_email(instance)
    
    
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profiles.save()

@receiver(pre_save, sender=Profile)
def profile_pre_save(sender, instance, **kwargs):
    """Send email notification when profile is updated"""
    if instance.pk:  # If profile already exists (update)
        old_profile = Profile.objects.get(pk=instance.pk)
        # Check if any important fields changed
        fields_to_check = ['bio', 'birth_date', 'phone_number']
        # if any(getattr(old_profile, field) != getattr(instance, field) for field in fields_to_check):
            # if instance.user.email:
            #     send_profile_update_email(instance.user)