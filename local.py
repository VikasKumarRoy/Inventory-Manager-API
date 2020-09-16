from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': <'YOUR_DATABASE_HERE'>,
        'USER': <'YOUR_USER_HERE'>,
        'PASSWORD': <'YOUR_PASSWORD_HERE'>,
        'HOST': 'localhost',
        'PORT': ''
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = <'YOUR_EMAIL_HERE'>
EMAIL_HOST_PASSWORD = <'YOUR_PASSWORD_HERE'>
