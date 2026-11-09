import secrets

from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from apps.core.models import SluggedModel, TimeStampedModel
from apps.core.utils import to_persian_digits

mobile_validator = RegexValidator(r"^09\d{9}$", "شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود.")


class ServiceQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class Service(SluggedModel):
    ICON_CHOICES = [
        ("wrench", "آچار (تعمیرات)"),
        ("oil", "روغن (سرویس دوره‌ای)"),
        ("gear", "چرخ‌دنده (مکانیک)"),
        ("battery", "باتری (برق خودرو)"),
        ("paint", "رنگ (صافکاری و نقاشی)"),
        ("shield", "سپر (گارانتی)"),
        ("car", "خودرو (فروش)"),
        ("tow", "امداد خودرو"),
        ("diag", "عیب‌یابی"),
    ]

    title = models.CharField("عنوان خدمت", max_length=150)
    icon = models.CharField("آیکون", max_length=20, choices=ICON_CHOICES, default="wrench")
    summary = models.TextField("خلاصه", max_length=400)
    body = CKEditor5Field("توضیحات کامل", config_name="extends", blank=True)
    image = models.ImageField("تصویر", upload_to="services/", blank=True)
    bookable = models.BooleanField("قابل انتخاب در فرم نوبت‌دهی", default=True)
    is_active = models.BooleanField("فعال", default=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    comments = GenericRelation("interactions.Comment")
    likes = GenericRelation("interactions.Like")

    objects = ServiceQuerySet.as_manager()

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "خدمت"
        verbose_name_plural = "خدمات"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("services:detail", kwargs={"slug": self.slug})


class AppointmentSlot(models.Model):
    """بازه‌های زمانی پذیرش؛ از پنل ادمین قابل تعریف است."""

    start_time = models.TimeField("ساعت شروع")
    end_time = models.TimeField("ساعت پایان")
    capacity = models.PositiveSmallIntegerField("ظرفیت پذیرش", default=3, help_text="حداکثر تعداد خودرو در این بازه")
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        ordering = ["start_time"]
        verbose_name = "بازه زمانی نوبت"
        verbose_name_plural = "بازه‌های زمانی نوبت"

    def __str__(self):
        return to_persian_digits(f"{self.start_time:%H:%M} تا {self.end_time:%H:%M}")


class ClosedDay(models.Model):
    date = models.DateField("تاریخ", unique=True)
    reason = models.CharField("علت", max_length=150, blank=True, help_text="مثلاً تعطیل رسمی")

    class Meta:
        ordering = ["date"]
        verbose_name = "روز تعطیل"
        verbose_name_plural = "روزهای تعطیل"

    def __str__(self):
        return f"{self.date} {self.reason}"


def generate_tracking_code():
    return "".join(secrets.choice("0123456789") for _ in range(8))


class Appointment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار تأیید"
        CONFIRMED = "confirmed", "تأیید شده"
        DONE = "done", "انجام شده"
        CANCELLED = "cancelled", "لغو شده"

    tracking_code = models.CharField("کد پیگیری", max_length=12, unique=True, editable=False)
    full_name = models.CharField("نام و نام خانوادگی", max_length=120)
    phone = models.CharField("شماره موبایل", max_length=11, validators=[mobile_validator])
    car_model = models.CharField("مدل خودرو", max_length=100)
    plate_number = models.CharField("شماره پلاک", max_length=30, blank=True)
    mileage = models.PositiveIntegerField("کارکرد (کیلومتر)", null=True, blank=True)
    service = models.ForeignKey(
        Service, verbose_name="نوع خدمت", on_delete=models.SET_NULL, null=True, related_name="appointments"
    )
    date = models.DateField("تاریخ مراجعه")
    slot = models.ForeignKey(
        AppointmentSlot, verbose_name="ساعت مراجعه", on_delete=models.SET_NULL, null=True, related_name="appointments"
    )
    description = models.TextField("شرح مشکل / توضیحات", blank=True)
    status = models.CharField("وضعیت", max_length=12, choices=Status.choices, default=Status.PENDING)
    admin_note = models.TextField("یادداشت پذیرش (به مشتری نمایش داده می‌شود)", blank=True)
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True, editable=False)

    class Meta:
        ordering = ["-date", "slot__start_time"]
        verbose_name = "نوبت"
        verbose_name_plural = "نوبت‌های تعمیرگاه"
        indexes = [models.Index(fields=["date", "status"])]

    def __str__(self):
        return f"{self.full_name} - {self.tracking_code}"

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            code = generate_tracking_code()
            while Appointment.objects.filter(tracking_code=code).exists():
                code = generate_tracking_code()
            self.tracking_code = code
        super().save(*args, **kwargs)
