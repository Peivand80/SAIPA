from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from apps.core.models import SluggedModel


class WarrantyPlan(SluggedModel):
    """طرح‌های گارانتی، کارت طلایی، بیمه بدنه و ... که از پنل ادمین تعریف می‌شوند."""

    ICON_CHOICES = [
        ("shield", "سپر"),
        ("card", "کارت"),
        ("doc", "سند"),
        ("clock", "ساعت"),
        ("star", "ستاره"),
    ]

    title = models.CharField("عنوان", max_length=150, help_text="مثلاً گارانتی محصولات، کارت طلایی")
    icon = models.CharField("آیکون", max_length=10, choices=ICON_CHOICES, default="shield")
    summary = models.TextField("خلاصه", max_length=400)
    body = CKEditor5Field("متن کامل (شرایط، مزایا، مدارک لازم)", config_name="extends")
    image = models.ImageField("تصویر", upload_to="warranty/", blank=True)
    highlights = models.TextField(
        "نکات کلیدی", blank=True, help_text="هر نکته در یک خط. به‌صورت لیست تیک‌دار نمایش داده می‌شود."
    )
    order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "طرح گارانتی / کارت طلایی"
        verbose_name_plural = "طرح‌های گارانتی و کارت طلایی"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("warranty:detail", kwargs={"slug": self.slug})


class FAQ(models.Model):
    plan = models.ForeignKey(
        WarrantyPlan, verbose_name="مربوط به طرح", on_delete=models.CASCADE, null=True, blank=True,
        related_name="faqs", help_text="اگر خالی باشد جزو سؤالات عمومی است.",
    )
    question = models.CharField("پرسش", max_length=300)
    answer = models.TextField("پاسخ")
    order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "پرسش متداول"
        verbose_name_plural = "پرسش‌های متداول"

    def __str__(self):
        return self.question
