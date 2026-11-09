"""
تنظیمات پایه پروژه سایت نمایندگی سایپا - جدیدالاسلامی
تنظیمات مخصوص محیط توسعه در dev.py و محیط واقعی در prod.py قرار دارد.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = False
ALLOWED_HOSTS: list[str] = []

# ---------------------------------------------------------------------------
# اپلیکیشن‌ها
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
]
THIRD_PARTY_APPS = [
    "django_ckeditor_5",
]
LOCAL_APPS = [
    "apps.core",
    "apps.catalog",
    "apps.services",
    "apps.parts",
    "apps.warranty",
    "apps.blog",
    "apps.interactions",
    "apps.contact",
    "apps.chatbot",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_context",
            ],
            "builtins": [
                "apps.core.templatetags.persian",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# پایگاه داده (در محیط توسعه SQLite؛ برای محیط واقعی PostgreSQL در prod.py)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# زبان و زمان
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "fa"
LANGUAGES = [("fa", "فارسی")]
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# فایل‌های استاتیک و رسانه
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# ---------------------------------------------------------------------------
# کش (برای محدود کردن ارسال پشت‌سرهم نظر و پیام)
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "saipa-site",
    }
}

MESSAGE_TAGS = {
    40: "error",
}

# ---------------------------------------------------------------------------
# تنظیمات اختصاصی سایت
# ---------------------------------------------------------------------------
PAGINATION = {
    "posts": 9,
    "cars": 9,
    "parts": 12,
    "services": 9,
    "comments": 10,
    "search": 10,
}

# حداکثر تعداد نظر یا پیام از یک IP در بازه زمانی (ثانیه)
FORM_THROTTLE = {"limit": 5, "window": 600}

# مدل‌هایی که کامنت و لایک برایشان فعال است
INTERACTION_MODELS = ["blog.post", "catalog.car", "services.service"]

# ---------------------------------------------------------------------------
# ویرایشگر CKEditor 5 (برای نوشتن مطالب و افزودن تصویر از پنل ادمین)
# ---------------------------------------------------------------------------
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "staff"
CKEDITOR_5_FILE_STORAGE = "apps.core.storage.EditorStorage"
CKEDITOR_5_UPLOAD_FILE_TYPES = ["jpeg", "jpg", "png", "gif", "webp"]
CKEDITOR_5_CONFIGS = {
    "default": {
        "language": "fa",
        "toolbar": [
            "heading", "|", "bold", "italic", "link", "bulletedList", "numberedList",
            "blockQuote", "imageUpload", "insertTable", "|", "undo", "redo",
        ],
    },
    "extends": {
        "language": "fa",
        "blockToolbar": [
            "paragraph", "heading1", "heading2", "heading3", "|",
            "bulletedList", "numberedList", "|", "blockQuote",
        ],
        "toolbar": [
            "heading", "|", "alignment", "bold", "italic", "underline", "link",
            "highlight", "|", "bulletedList", "numberedList", "outdent", "indent", "|",
            "blockQuote", "imageUpload", "insertTable", "mediaEmbed", "horizontalLine", "|",
            "removeFormat", "sourceEditing", "|", "undo", "redo",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative", "|", "imageStyle:alignLeft", "imageStyle:alignRight",
                "imageStyle:alignCenter", "imageStyle:side", "|", "toggleImageCaption",
            ],
            "styles": ["full", "side", "alignLeft", "alignRight", "alignCenter"],
        },
        "table": {
            "contentToolbar": ["tableColumn", "tableRow", "mergeTableCells", "tableProperties", "tableCellProperties"],
        },
        "heading": {
            "options": [
                {"model": "paragraph", "title": "پاراگراف", "class": "ck-heading_paragraph"},
                {"model": "heading2", "view": "h2", "title": "تیتر ۲", "class": "ck-heading_heading2"},
                {"model": "heading3", "view": "h3", "title": "تیتر ۳", "class": "ck-heading_heading3"},
                {"model": "heading4", "view": "h4", "title": "تیتر ۴", "class": "ck-heading_heading4"},
            ]
        },
    },
}
