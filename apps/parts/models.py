from django.db import models
from django.urls import reverse

from apps.catalog.models import Car
from apps.core.models import SluggedModel, TimeStampedModel
from apps.services.models import mobile_validator


class PartCategory(SluggedModel):
    title = models.CharField("عنوان", max_length=100, help_text="مثلاً موتوری، برقی، بدنه، مصرفی")
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "دسته‌بندی قطعه"
        verbose_name_plural = "دسته‌بندی‌های قطعات"

    def __str__(self):
        return self.title


class Part(SluggedModel):
    class Stock(models.TextChoices):
        AVAILABLE = "available", "موجود"
        ORDER = "order", "سفارشی"
        UNAVAILABLE = "unavailable", "ناموجود"

    title = models.CharField("نام قطعه", max_length=200)
    code = models.CharField("کد فنی قطعه", max_length=60, blank=True, db_index=True)
    category = models.ForeignKey(
        PartCategory, verbose_name="دسته‌بندی", on_delete=models.SET_NULL, null=True, blank=True, related_name="parts"
    )
    cars = models.ManyToManyField(Car, verbose_name="خودروهای سازگار", blank=True, related_name="parts")
    image = models.ImageField("تصویر", upload_to="parts/", blank=True)
    description = models.TextField("توضیحات", blank=True)
    price = models.PositiveBigIntegerField("قیمت (تومان)", null=True, blank=True, help_text="خالی = «استعلام بگیرید»")
    stock = models.CharField("وضعیت موجودی", max_length=12, choices=Stock.choices, default=Stock.AVAILABLE)
    is_genuine = models.BooleanField("قطعه اصلی (جنیون)", default=True)
    is_active = models.BooleanField("نمایش در سایت", default=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "قطعه"
        verbose_name_plural = "قطعات"

    def __str__(self):
        return f"{self.title} ({self.code})" if self.code else self.title

    def get_absolute_url(self):
        return reverse("parts:detail", kwargs={"slug": self.slug})


class PartInquiry(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "جدید"
        ANSWERED = "answered", "پاسخ داده شد"
        CLOSED = "closed", "بسته شد"

    part = models.ForeignKey(Part, verbose_name="قطعه", on_delete=models.SET_NULL, null=True, blank=True)
    part_name = models.CharField("نام قطعه درخواستی", max_length=200)
    car_model = models.CharField("مدل خودرو", max_length=100)
    full_name = models.CharField("نام", max_length=120)
    phone = models.CharField("شماره موبایل", max_length=11, validators=[mobile_validator])
    message = models.TextField("توضیحات", blank=True)
    status = models.CharField("وضعیت", max_length=10, choices=Status.choices, default=Status.NEW)
    admin_note = models.TextField("یادداشت داخلی", blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "استعلام قطعه"
        verbose_name_plural = "استعلام‌های قطعه"

    def __str__(self):
        return f"{self.part_name} - {self.full_name}"
