# -*- encoding: utf-8 -*-

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'hattori',
    'tests'
]

MIDDLEWARE = []

USE_TZ = True

SECRET_KEY = 'foobar'

LANGUAGE_CODE = 'en-us'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
}]


STATIC_URL = '/static/'

ANONYMIZE_ENABLED = True
