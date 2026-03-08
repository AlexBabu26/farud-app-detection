from pathlib import Path
from datetime import timedelta
import os

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env: try project root first, then current working directory
try:
    from dotenv import load_dotenv
    env_file = BASE_DIR / ".env"
    load_dotenv(str(env_file))  # str() for compatibility on Windows paths with spaces
    if not (os.getenv("GROQ_API_KEY") or "").strip():
        load_dotenv()  # fallback: .env in current working directory
except ImportError:
    pass

# Last resort: read key vars from .env file if still missing (e.g. dotenv path issues)
def _read_env_line(key: str) -> str:
    try:
        with open(BASE_DIR / ".env", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(key + "=") and not line.startswith("#"):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return ""
for _key in ("GROQ_API_KEY", "GROQ_MODEL"):
    if not (os.getenv(_key) or "").strip():
        _val = _read_env_line(_key)
        if _val:
            os.environ[_key] = _val

# ------------------------------------------------------------
# Security / Environment (set in .env; see .env.example)
# ------------------------------------------------------------
_SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
# Require SECRET_KEY in production; allow dev fallback when DEBUG is on
if not _SECRET_KEY and DEBUG:
    _SECRET_KEY = "django-insecure-dev-only-change-in-production"
SECRET_KEY = _SECRET_KEY

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# Optional but recommended for local development
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

# ------------------------------------------------------------
# Application definition
# ------------------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    # If you want JWT blacklisting features, also add:
    # "rest_framework_simplejwt.token_blacklist",

    # Local apps
    "apps.accounts",
    "apps.apps_store",
    "apps.reviews",
    "apps.analysis",
    "apps.frontend",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fraud_app_detector.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # optional (if you add global templates later)
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

WSGI_APPLICATION = "fraud_app_detector.wsgi.application"

# ------------------------------------------------------------
# Database (SQLite)
# ------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ------------------------------------------------------------
# Password validation
# ------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------
# Internationalization
# ------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------
# Static files
# ------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ------------------------------------------------------------
# Default primary key field type
# ------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------
# Django REST Framework configuration
# ------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
        "analysis": os.getenv("ANALYSIS_THROTTLE_RATE", "10/hour"),
    },
}

# ------------------------------------------------------------
# SimpleJWT configuration
# ------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "30"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",

    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",

    # Optional: reduce token bloat unless you need these:
    # "TOKEN_TYPE_CLAIM": "token_type",
    # "JTI_CLAIM": "jti",
}

# ------------------------------------------------------------
# Groq configuration (used by analysis app; set in .env)
# ------------------------------------------------------------
GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile").strip()

# ------------------------------------------------------------
# Basic logging (useful for debugging API issues)
# ------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
}
