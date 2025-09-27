from pathlib import Path
import os
from dotenv import load_dotenv
# Load environment variables from the .env file
load_dotenv()
# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Secret Key
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-fallback-secret-key")

# Debug Mode (Set to False in production)
DEBUG = os.environ.get("DEBUG", "False") == "True"

# Allowed Hosts
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Add the scheme (https://) to the ALLOWED_HOSTS for CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = []

# f"https://{host}" if not host.startswith("http") else host for host in ALLOWED_HOSTS
for host in ALLOWED_HOSTS:
    CSRF_TRUSTED_ORIGINS.append(f'http://{host}')
    CSRF_TRUSTED_ORIGINS.append(f'https://{host}')
    

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    

    # Local apps
    'apps.core',
    'apps.authentication',
    'apps.hiring',
    'apps.jobs',
    'apps.depts',
    'apps.integrations',

    # Third-party apps
    'django_bootstrap5',
]

# Enable DRF only if REST_ENABLED=True in .env
if os.environ.get("REST_ENABLED", "False") == "True":
    INSTALLED_APPS += [
        'rest_framework',
    ]

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.BasicAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
    }


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.CustomErrorMiddleware'
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.project_details'
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database (default SQLite; overridden in production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'django_db'),
        'USER': os.environ.get('DB_USER', 'django'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'django'),
        'HOST': os.environ.get('DB_HOST', 'db'),  # matches your docker-compose service name
        'PORT': os.environ.get('DB_PORT', 5432),
    }
}

# Origin
CSRF_COOKIE_SAMESITE = 'Lax'  # or 'Strict'
CSRF_COOKIE_SECURE = True  # Only send the CSRF cookie over HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and Media Files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'authentication.CustomUser'

PROJECT_NAME = 'Django Boilerplate'


# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Hardcoded
EMAIL_PORT = 587  # Hardcoded
EMAIL_USE_TLS = True  # Hardcoded
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')  # Read from .env
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')  # Read from .env
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'no-reply@example.com')  # Read from .env or default fallback



LOGIN_REDIRECT_URL = '/'  # Redirect to the home page after login
LOGIN_URL = '/auth/login'  # URL name for the login view
LOGOUT_REDIRECT_URL = '/auth/login'  # Redirect to the home page after logout






# API KEYS

# Google Calendar
GOOGLE_CALENDAR_CLIENT_ID = os.environ.get("GOOGLE_CALENDAR_CLIENT_ID")
GOOGLE_CALENDAR_CLIENT_SECRET = os.environ.get("GOOGLE_CALENDAR_CLIENT_SECRET")
GOOGLE_CALENDAR_REDIRECT_URI = os.environ.get("GOOGLE_CALENDAR_REDIRECT_URI")

# Google Maps
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

# Twilio
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM_PHONE_NUMBER = os.environ.get("TWILIO_FROM_PHONE_NUMBER")