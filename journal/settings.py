from pathlib import Path
import os
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent

# CONTENT_DIR = os.path.join(BASE_DIR, '/home/oneckico/public_html/content')
CONTENT_DIR = os.path.join(BASE_DIR, 'content')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-moars5!_lkdd1be(s@dq(xzx$9c)qv@9pelo_5z3t(_)j6(0g'

# SECURITY WARNING: don't run with debug turned on in production!
# For prod, debug state will change
# DEBUG = False
DEBUG = True

# ALLOWED_HOSTS = ["domain_name.com","www.domain_name.com"]
ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'crispy_forms',
    'django_editorjs',
    'accounts',
    'hitcount',
    'home',
    'django_seed',
    'django_social_share',
    'journalApp',
    "bootstrap4",
    'import_export',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'journal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'journal.wsgi.application'

# email backend user and password needed :)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # new
EMAIL_HOST_USER = ''  # new
EMAIL_HOST_PASSWORD = ''  # new
EMAIL_PORT = 587  # new
EMAIL_USE_TLS = True  # new

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# backend for postgresql db

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': '',
#         'USER': '',
#         'PASSWORD': '',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = "accounts.CustomUser"

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Istanbul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


ENABLE_USER_ACTIVATION = True
ENABLE_ACTIVATION_AFTER_EMAIL_CHANGE = True
DISABLE_USERNAME = False
LOGIN_VIA_EMAIL = False
LOGIN_VIA_EMAIL_OR_USERNAME = True
LOGIN_REDIRECT_URL = 'index'
LOGIN_URL = 'accounts:log_in'
USE_REMEMBER_ME = False

RESTORE_PASSWORD_VIA_EMAIL_OR_USERNAME = True
EMAIL_ACTIVATION_AFTER_CHANGING = True

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

LANGUAGES = [
    ('en', _('English')),
    ('tr', _('Türkçe')),
    ('ru', _('Russian')),
    ('zh-Hans', _('Chinese')),
]


# STATIC_ROOT = '/home/oneckico/public_html/content/static/'
# MEDIA_ROOT = '/home/oneckico/public_html/content/media/'
#
# STATIC_URL = '/content/static/'
# MEDIA_URL = '/content/media/'


STATIC_ROOT = 'content/static/'
STATIC_URL = '/content/static/'
MEDIA_ROOT = 'content/media/'
MEDIA_URL = '/content/media/'

STATICFILES_DIRS = [
    os.path.join(CONTENT_DIR, 'staticfiles'),
]

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, '../locale'),

)

SIGN_UP_FIELDS = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
if DISABLE_USERNAME:
    SIGN_UP_FIELDS = ['first_name', 'last_name', 'email', 'password1', 'password2']

CRISPY_TEMPLATE_PACK = "bootstrap4"
