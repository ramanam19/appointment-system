from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['kartik1910.pythonanywhere.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'kartik1910$appointment_DB',
        'USER': 'kartik1910',
        'PASSWORD': 'Kartik123456',
        'HOST': 'kartik1910.mysql.pythonanywhere-services.com',
    }
}