from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_stage_completion_email(user, stage, course):
    """
    Send congratulations email when user completes a course stage
    """
    # Calculate progress
    total_stages = course.stage_set.count()
    completed_stages = user.completed_stages.filter(course=course).count()
    progress = (completed_stages / total_stages) * 100 if total_stages > 0 else 0
    
    # Get next stage if available
    next_stage = course.stage_set.filter(order__gt=stage.order).first()
    next_stage_name = next_stage.name if next_stage else "Curso Concluído!"
    
    subject = f'Parabéns! Você concluiu uma etapa em {course.name}'
    html_message = render_to_string('emails/stage_completion.html', {
        'user': user,
        'stage_name': stage.name,
        'course_name': course.name,
        'progress': round(progress, 1),
        'next_stage': next_stage_name
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