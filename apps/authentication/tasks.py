import pytz
from decouple import config
from datetime import datetime
from celery import shared_task
from django.core.mail import send_mail
from core.settings import EMAIL_HOST_USER
# TODO: Implement email templates


@shared_task(bind=True)
def send_celery_task(self, subject, message, author, recipient_list):
    send_mail(subject, message, author, recipient_list, fail_silently=True)
    return 'Done!'


@shared_task(bind=True)
def confirm_register_email(self, email, token):
    subject = 'Register confirmation'

    message = (f'Hello! Please click the link below to confirm your email.\n\n'
               f'{config("WEBSITE_URL")}/validate/{token}\n\n'
               f'If you did not request this, please ignore this email.\n\n'
               f'Thanks, Infinite Foundry.')

    email_from = EMAIL_HOST_USER
    to_email = [email]
    send_celery_task.delay(subject, message, email_from, to_email)


@shared_task(bind=True)
def reset_password_email(self, username, token):
    subject = 'Password reset'

    message = (f'Hello! Please click the link below to reset your password.\n\n'
               f'{config("WEBSITE_URL")}/reset-password/{token}\n\n'
               f'If you did not request this, please ignore this email.\n\n'
               f'Thanks, Infinite Foundry.')

    email_from = EMAIL_HOST_USER
    to_email = [username]
    send_celery_task.delay(subject, message, email_from, to_email)


@shared_task(bind=True)
def reset_password_confirmation_email(self, username):
    subject = 'Password changed'

    date = datetime.now(tz=pytz.utc).strftime("%d/%m/%Y %H:%M:%S")

    message = (f'Hello! Your password has been changed at {date} UTC.\n\n'
               f'If you did not request this, please contact us.\n\n'
               f'Thanks, Infinite Foundry.')

    email_from = EMAIL_HOST_USER
    to_email = [username]
    send_celery_task.delay(subject, message, email_from, to_email)
