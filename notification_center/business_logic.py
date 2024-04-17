import os

from dotenv import load_dotenv  # need for correct work os.environ.get()
from django.core.mail import send_mail
from django.template.loader import render_to_string

from celery_app.celery import app

load_dotenv()


@app.task
def send_email(message, recipient_list, html_message=None, context=None):
    if html_message:
        html_message = render_to_string(html_message, context=context)

    email = {
        'subject': 'Web_Menu_DA',
        'message': message,
        'from_email': os.environ.get('auth_user'),
        'recipient_list': recipient_list,
        'fail_silently': False,
        'auth_user': os.environ.get('auth_user'),
        'auth_password': os.environ.get('email_token'),
        'html_message': html_message,
    }
    send_mail(**email)
