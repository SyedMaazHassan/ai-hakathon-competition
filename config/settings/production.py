from .base import *

DEBUG = os.environ.get("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "your-production-domain.com").split(",")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("DB_NAME", "your_db_name"),
        'USER': os.environ.get("DB_USER", "your_db_user"),
        'PASSWORD': os.environ.get("DB_PASSWORD", "your_db_password"),
        'HOST': os.environ.get("DB_HOST", "localhost"),
        'PORT': os.environ.get("DB_PORT", "5432"),
    }
}
