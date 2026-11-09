"""
راه‌اندازی اولیه تنظیمات سایت (بدون ساخت مطلب یا محتوای نمونه).
اجرا: python manage.py init_site
"""
import datetime

from django.core.management.base import BaseCommand

from apps.core.models import SiteSettings
from apps.services.models import AppointmentSlot

DEFAULT_SLOTS = [(8, 10), (10, 12), (12, 14), (14, 16)]


class Command(BaseCommand):
    help = "ساخت تنظیمات پیش‌فرض سایت و بازه‌های زمانی نوبت‌دهی"

    def handle(self, *args, **options):
        SiteSettings.load()
        self.stdout.write(self.style.SUCCESS("✓ تنظیمات سایت آماده است."))

        if AppointmentSlot.objects.exists():
            self.stdout.write("• بازه‌های زمانی نوبت قبلاً تعریف شده‌اند؛ تغییری داده نشد.")
        else:
            for start, end in DEFAULT_SLOTS:
                AppointmentSlot.objects.create(start_time=datetime.time(start), end_time=datetime.time(end), capacity=3)
            self.stdout.write(self.style.SUCCESS("✓ چهار بازه زمانی پیش‌فرض نوبت (۸ تا ۱۶) ساخته شد."))
