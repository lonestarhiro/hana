from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#ホスト
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LINE_TOKEN = "f8bzQHIjpAi1vnE5jZAhSszwYxHK1MW5qH9N76IoJFr" #to 春日個人
