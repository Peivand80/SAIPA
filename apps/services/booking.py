"""منطق محاسبه روزها و بازه‌های قابل رزرو نوبت."""
import datetime

from django.db.models import Count, Q
from django.utils import timezone

from apps.core.models import SiteSettings
from apps.core.templatetags.persian import jdate, weekday_fa

from .models import Appointment, AppointmentSlot, ClosedDay


def available_dates():
    """لیست روزهای کاری قابل رزرو از امروز تا N روز آینده."""
    site = SiteSettings.load()
    today = timezone.localdate()
    closed = set(
        ClosedDay.objects.filter(date__gte=today, date__lte=today + datetime.timedelta(days=60)).values_list("date", flat=True)
    )
    days = []
    for i in range(site.appointment_days_ahead + 1):
        day = today + datetime.timedelta(days=i)
        if day in closed:
            continue
        if site.closed_on_friday and day.weekday() == 4:
            continue
        if site.closed_on_thursday and day.weekday() == 3:
            continue
        days.append(day)
    return days


def date_label(day):
    today = timezone.localdate()
    prefix = "امروز - " if day == today else ("فردا - " if day == today + datetime.timedelta(days=1) else "")
    return f"{prefix}{weekday_fa(day)} {jdate(day, '%d %B')}"


def slot_availability(day):
    """ظرفیت باقی‌مانده هر بازه زمانی در یک روز مشخص."""
    now = timezone.localtime()
    slots = AppointmentSlot.objects.filter(is_active=True).annotate(
        booked=Count(
            "appointments",
            filter=Q(appointments__date=day) & ~Q(appointments__status=Appointment.Status.CANCELLED),
        )
    )
    result = []
    for slot in slots:
        remaining = max(slot.capacity - slot.booked, 0)
        passed = day == now.date() and slot.start_time <= now.time()
        result.append({
            "slot": slot,
            "id": slot.pk,
            "label": str(slot),
            "remaining": remaining,
            "available": remaining > 0 and not passed,
            "passed": passed,
        })
    return result
