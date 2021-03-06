"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
import django
import os

from django.utils.encoding import force_str

from corsheaders.defaults import default_headers


django.utils.encoding.force_text = force_str


APP_DOMAIN = os.environ.get("APP_DOMAIN")
APP_ENV = os.environ.get("APP_ENV")
APP_NAME = os.environ.get("APP_NAME")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

WSGI_APPLICATION = "app.wsgi.application"


# Application definition

# Multitenancy
# https://django-tenants.readthedocs.io/en/latest/

SHARED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "corsheaders",
    "django_tenants",
    "safedelete",
    "tenant",
)

DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

PUBLIC_SCHEMA_NAME = "public"

TENANT_APPS = (
    "account",
    "organization",
)

TENANT_DOMAIN_MODEL = "tenant.Domain"

TENANT_MODEL = "tenant.Tenant"

INSTALLED_APPS = list(SHARED_APPS) + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]


# Route
# https://docs.djangoproject.com/en/4.0/topics/http/urls/

ROOT_URLCONF = "app.urls"
APPEND_SLASH = False


# ALLOWED_HOSTS
# https://docs.djangoproject.com/en/4.0/ref/settings/#allowed-hosts

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")


# Middleware
# https://docs.djangoproject.com/en/4.0/topics/http/middleware/

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "core.middleware.HealthCheckMiddleware",
    "tenant.middleware.XTenantMiddleware",
    "django_tenants.middleware.main.TenantMainMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("SQL_USER"),
        "PASSWORD": os.environ.get("SQL_PASSWORD"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}


# CORS
# https://pypi.org/project/django-cors-headers/

CORS_URLS_REGEX = r"^/api/.*$"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://\w+\.localhost:3000$",
    r"^http://\w+\.localhost:8000$",
]

CORS_ALLOW_METHODS = [
    "GET",
    "OPTIONS",
    "POST",
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "X-Tenant",
]


# GraphQL
# https://docs.graphene-python.org/en/latest/quickstart/
# https://django-graphql-jwt.domake.io/

GRAPHENE = {
    "ATOMIC_MUTATIONS": True,
    "SCHEMA": "django_root.schema.schema",
    "MIDDLEWARE": [
        "core.graphql_jwt.middleware.JSONWebTokenMiddleware",
    ],
}

GRAPHQL_JWT = {
    "JWT_ALLOW_ARGUMENT": True,
    "JWT_ALLOW_REFRESH": True,
    "JWT_PAYLOAD_HANDLER": "core.graphql_jwt.utils.jwt_payload",
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_LONG_RUNNING_REFRESH_TOKEN": True,
    "JWT_EXPIRATION_DELTA": timedelta(
        minutes=int(os.environ["JWT_EXPIRATION_MINUTES"])
    ),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(
        days=int(os.environ["JWT_REFRESH_EXPIRATION_DAYS"])
    ),
    "JWT_SECRET_KEY": SECRET_KEY,
    "JWT_ALGORITHM": "HS256",
}


# Authentication
# https://docs.djangoproject.com/en/4.0/topics/auth/

AUTH_USER_MODEL = "account.User"

AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]


# Templates
# https://docs.djangoproject.com/en/4.0/topics/templates/

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
