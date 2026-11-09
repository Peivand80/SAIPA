"""تنظیمات محیط توسعه (لوکال‌هاست)."""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]

# در محیط توسعه ایمیل‌ها در ترمینال چاپ می‌شوند
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
