from django.core.mail import get_connection, EmailMultiAlternatives
import uuid


def generate_key():
    return uuid.uuid4().hex


def send_mass_html_mail(datatuple, fail_silently=False):
    connection = get_connection(fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)

