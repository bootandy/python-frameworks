DATABASES = {
    'default' : {
        'ENGINE': 'django_mongodb_engine',
        'NAME': 'houseprices',
        'HOST': '192.168.1.68'
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',

    'hp',
]
MIDDLEWARE_CLASSES = [
  #'django.middleware.csrf.CsrfViewMiddleware'
]

ROOT_URLCONF = 'urls'

DEBUG = TEMPLATE_DEBUG = True
