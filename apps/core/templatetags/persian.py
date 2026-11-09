"""
فیلترها و تگ‌های قالب برای نمایش فارسی (تاریخ شمسی، اعداد فارسی، قیمت).
این کتابخانه در settings به‌صورت builtin ثبت شده و نیازی به load ندارد.
"""
import datetime

import jdatetime
from django import template
from django.utils import timezone

from apps.core.utils import to_persian_digits

register = template.Library()

WEEKDAYS = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]


def to_jalali(value):
    if value is None or value == "":
        return None
    if isinstance(value, datetime.datetime):
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return jdatetime.datetime.fromgregorian(datetime=value, locale="fa_IR")
    if isinstance(value, datetime.date):
        return jdatetime.date.fromgregorian(date=value, locale="fa_IR")
    return None


@register.filter
def jdate(value, fmt="%d %B %Y"):
    """تاریخ میلادی را به شمسی تبدیل می‌کند: {{ post.created_at|jdate }}"""
    j = to_jalali(value)
    if j is None:
        return ""
    return to_persian_digits(j.strftime(fmt))


@register.filter
def jdatetime_full(value):
    return jdate(value, "%d %B %Y - %H:%M")


@register.filter
def weekday_fa(value):
    if isinstance(value, datetime.datetime):
        value = timezone.localtime(value).date() if timezone.is_aware(value) else value.date()
    if isinstance(value, datetime.date):
        return WEEKDAYS[value.weekday()]
    return ""


@register.filter
def fa_num(value):
    """اعداد را فارسی می‌کند: {{ 123|fa_num }} → ۱۲۳"""
    if value is None:
        return ""
    return to_persian_digits(value)


@register.filter
def money(value):
    """عدد را با جداکننده هزارگان و ارقام فارسی نمایش می‌دهد."""
    if value in (None, ""):
        return ""
    try:
        return to_persian_digits(f"{int(value):,}").replace(",", "٬")
    except (TypeError, ValueError):
        return to_persian_digits(value)


@register.simple_tag
def jalali_year():
    return to_persian_digits(jdatetime.date.today().year)


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """پارامترهای فعلی آدرس را حفظ و فقط موارد داده‌شده را عوض می‌کند (برای صفحه‌بندی)."""
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            query.pop(key, None)
        else:
            query[key] = value
    return query.urlencode()


@register.filter
def linebreaks_list(value):
    """متن چندخطی را به لیست خطوط تبدیل می‌کند."""
    if not value:
        return []
    return [line.strip() for line in str(value).splitlines() if line.strip()]
