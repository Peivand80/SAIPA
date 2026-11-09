from django.db import models

from apps.core.models import TimeStampedModel


class ContactMessage(TimeStampedModel):
    class Subject(models.TextChoices):
        SALES = "sales", "فروش و شرایط خرید"
        SERVICE = "service", "خدمات پس از فروش"
        PARTS = "parts", "قطعات یدکی"
        WARRANTY = "warranty", "گارانتی و کارت طلایی"
        COMPLAINT = "complaint", "انتقاد و شکایت"
        SUGGESTION = "suggestion", "پیشنهاد"
        OTHER = "other", "سایر"

    full_name = models.CharField("نام و نام خانوادگی", max_length=120)
    phone = models.CharField("تلفن تماس", max_length=20)
    email = models.EmailField("ایمیل", blank=True)
    subject = models.CharField("موضوع", max_length=12, choices=Subject.choices, default=Subject.OTHER)
    message = models.TextField("متن پیام", max_length=3000)
    is_read = models.BooleanField("خوانده شده", default=False)
    admin_note = models.TextField("یادداشت داخلی / پاسخ", blank=True)
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True, editable=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "پیام"
        verbose_name_plural = "پیام‌های تماس با ما"

    def __str__(self):
        return f"{self.full_name} - {self.get_subject_display()}"
