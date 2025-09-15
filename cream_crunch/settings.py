from pathlib import Path
import os
<<<<<<< Updated upstream
=======
import django

# JSONField import for compatibility
if django.VERSION < (3, 1):
    from django.db.models import JSONField
else:
    from django.db.models import JSONField
>>>>>>> Stashed changes

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings
SECRET_KEY = 'django-insecure-@#$lk6x%t-$t3=3)d^6sh#q8-w4s2yg=+p=fuvp*rl7pl#f#o%'
DEBUG = True
ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bakery',
<<<<<<< Updated upstream
]

=======
    'django.contrib.sites',

    # allauth apps (conditionally for dev)
    # Disable socialaccount if using SQLite to avoid JSONField errors
]

# Social apps removed for SQLite dev; enable later with PostgreSQL
# 'allauth',
# 'allauth.account',
# 'allauth.socialaccount',
# 'allauth.socialaccount.providers.google',

SITE_ID = 1

>>>>>>> Stashed changes
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'allauth.account.middleware.AccountMiddleware',  # Only if social login enabled
]

ROOT_URLCONF = 'cream_crunch.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # required for allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

<<<<<<< Updated upstream
WSGI_APPLICATION = 'cream_crunch.wsgi.application'
=======
ZEROBOUNCE_API_KEY = "807c9108ede34ee897d8ce15ca92f109"
>>>>>>> Stashed changes

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

<<<<<<< Updated upstream
=======
# Custom User
AUTH_USER_MODEL = 'bakery.CustomUser'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # default
    # 'allauth.account.auth_backends.AuthenticationBackend',  # Only if social login enabled
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
>>>>>>> Stashed changes

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

<<<<<<< Updated upstream
=======
# Social login providers (disabled for SQLite)
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'APP': {
            'client_id': 'YOUR_CLIENT_ID_HERE',
            'secret': 'YOUR_CLIENT_SECRET_HERE',
            'key': ''
        }
    }
}
>>>>>>> Stashed changes

# Static & Media
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
<<<<<<< Updated upstream
# Optional (if you keep a custom folder for static files inside your app/project)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
=======

# # Email
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_USE_TLS = True
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'sambhavmurabiya@gmail.com'
# EMAIL_HOST_PASSWORD = '123'  # App password, NOT your main password
>>>>>>> Stashed changes
