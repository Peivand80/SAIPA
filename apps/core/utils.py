"""ابزارهای مشترک بین اپ‌ها."""
from django.conf import settings
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.text import slugify

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
LATIN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def to_persian_digits(value) -> str:
    return str(value).translate(PERSIAN_DIGITS)


def to_latin_digits(value) -> str:
    return str(value).translate(LATIN_DIGITS)


def unique_slugify(instance, value, slug_field="slug", max_length=200):
    """یک اسلاگ یکتا (با پشتیبانی از حروف فارسی) برای نمونه مدل می‌سازد."""
    # نیم‌فاصله به خط تیره تبدیل می‌شود تا اسلاگ خوانا بماند (عیب‌یابی ← عیب-یابی)
    value = str(value).replace("\u200c", "-")
    base = slugify(value, allow_unicode=True)[:max_length].strip("-") or "item"
    slug = base
    model = instance.__class__
    n = 2
    while model.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        suffix = f"-{n}"
        slug = f"{base[: max_length - len(suffix)]}{suffix}"
        n += 1
    return slug


def paginate(request, queryset, per_page_key, page_param="page"):
    """صفحه‌بندی یکسان در کل سایت؛ تعداد در هر صفحه از settings.PAGINATION خوانده می‌شود."""
    per_page = settings.PAGINATION.get(per_page_key, 10)
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get(page_param, 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


def get_client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def is_throttled(request, scope: str) -> bool:
    """
    اگر یک IP در بازه زمانی مشخص بیش از حد مجاز فرم ارسال کرده باشد True برمی‌گرداند.
    برای جلوگیری از اسپم در نظرات، پیام‌ها و نوبت‌دهی.
    """
    conf = settings.FORM_THROTTLE
    key = f"throttle:{scope}:{get_client_ip(request)}"
    count = cache.get(key, 0)
    if count >= conf["limit"]:
        return True
    cache.set(key, count + 1, conf["window"])
    return False
