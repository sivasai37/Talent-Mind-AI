"""
Django settings for HireGenius AI.
"""
import os
import warnings
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

_DEFAULT_SECRET = "hiregenius-dev-secret-key-CHANGE-ME-in-production"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", _DEFAULT_SECRET)

DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"

if not DEBUG and SECRET_KEY == _DEFAULT_SECRET:
    raise ValueError("DJANGO_SECRET_KEY must be set in production when DEBUG=False!")

raw_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
if raw_hosts:
    ALLOWED_HOSTS = [host.strip() for host in raw_hosts.split(",") if host.strip()]
else:
    ALLOWED_HOSTS = ["*"] if DEBUG else []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "api",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

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

WSGI_APPLICATION = "core.wsgi.application"

import dj_database_url

# Database: defaults to SQLite for instant run; switch to PostgreSQL via env.
if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif os.environ.get("USE_POSTGRES", "False").lower() == "true":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "hiregenius"),
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
    },
}

# CORS - restrict in production
if DEBUG or os.environ.get("CORS_ALLOW_ALL_ORIGINS", "False").lower() == "true":
    CORS_ALLOW_ALL_ORIGINS = True
else:
    raw_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    if raw_origins:
        CORS_ALLOWED_ORIGINS = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    else:
        CORS_ALLOWED_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]

# ---- HireGenius AI configuration ----
FAISS_INDEX_DIR = PROJECT_ROOT / "faiss_index"
EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"
EXPORTS_DIR = PROJECT_ROOT / "exports"
DATA_DIR = PROJECT_ROOT / "data"
for _d in (FAISS_INDEX_DIR, EMBEDDINGS_DIR, EXPORTS_DIR, DATA_DIR):
    _d.mkdir(parents=True, exist_ok=True)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

# Max input lengths for security
MAX_JD_LENGTH = int(os.environ.get("MAX_JD_LENGTH", 20000))
MAX_TOP_K = int(os.environ.get("MAX_TOP_K", 100))

# Hybrid ranking weights — overridden dynamically by role type
RANKING_WEIGHTS = {
    "semantic": 0.30,
    "skill": 0.30,
    "experience": 0.20,
    "recruitability": 0.10,
    "llm": 0.10,
}

# Role-aware dynamic weight configurations
ROLE_WEIGHTS = {
    "backend": {
        "semantic": 0.25,
        "skill": 0.35,
        "experience": 0.20,
        "recruitability": 0.10,
        "llm": 0.10,
    },
    "frontend": {
        "semantic": 0.25,
        "skill": 0.35,
        "experience": 0.20,
        "recruitability": 0.10,
        "llm": 0.10,
    },
    "leadership": {
        "semantic": 0.20,
        "skill": 0.20,
        "experience": 0.35,
        "recruitability": 0.15,
        "llm": 0.10,
    },
    "research": {
        "semantic": 0.40,
        "skill": 0.20,
        "experience": 0.15,
        "recruitability": 0.10,
        "llm": 0.15,
    },
    "data": {
        "semantic": 0.30,
        "skill": 0.30,
        "experience": 0.20,
        "recruitability": 0.10,
        "llm": 0.10,
    },
    "design": {
        "semantic": 0.30,
        "skill": 0.25,
        "experience": 0.20,
        "recruitability": 0.15,
        "llm": 0.10,
    },
    "general": {
        "semantic": 0.30,
        "skill": 0.30,
        "experience": 0.20,
        "recruitability": 0.10,
        "llm": 0.10,
    },
}

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "False").lower() == "true"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Production Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
