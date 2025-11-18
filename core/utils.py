from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_welcome_email(user):
    """
    Send welcome email to newly registered users
    """
    subject = 'Bem-vindo ao UmbuLearning!'
    html_message = render_to_string('emails/welcome_email.html', {
        'user': user
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_profile_update_email(user):
    """
    Send notification when user profile is updated
    """
    subject = 'Seu perfil foi atualizado - UmbuLearning'
    html_message = render_to_string('emails/profile_update.html', {
        'user': user
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )
