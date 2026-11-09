from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from apps.core.models import SluggedModel


class CarCategory(SluggedModel):
    title = models.CharField("عنوان", max_length=100, help_text="مثلاً سواری، وانت، شاسی‌بلند")
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "دسته‌بندی خودرو"
        verbose_name_plural = "دسته‌بندی‌های خودرو"

    def __str__(self):
        return self.title


class CarQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class Car(SluggedModel):
    title = models.CharField("نام خودرو", max_length=150)
    category = models.ForeignKey(
        CarCategory, verbose_name="دسته‌بندی", on_delete=models.SET_NULL, null=True, blank=True, related_name="cars"
    )
    tagline = models.CharField("شعار کوتاه", max_length=200, blank=True)
    summary = models.TextField("خلاصه معرفی", max_length=500, help_text="در کارت‌ها و لیست محصولات نمایش داده می‌شود.")
    description = CKEditor5Field("معرفی کامل", config_name="extends", blank=True)
    image = models.ImageField("تصویر اصلی", upload_to="cars/")
    price_text = models.CharField(
        "قیمت / وضعیت فروش", max_length=150, blank=True,
        help_text="مثلاً: قیمت کارخانه ۱٬۲۰۰٬۰۰۰٬۰۰۰ ریال یا «طبق اطلاعیه فروش»",
    )
    sale_link = models.URLField("لینک سامانه فروش رسمی", blank=True)
    brochure = models.FileField("کاتالوگ (PDF)", upload_to="cars/brochures/", blank=True)
    is_featured = models.BooleanField("نمایش در صفحه خانه", default=False)
    is_active = models.BooleanField("فعال", default=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    comments = GenericRelation("interactions.Comment")
    likes = GenericRelation("interactions.Like")

    objects = CarQuerySet.as_manager()

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "خودرو"
        verbose_name_plural = "خودروها"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("catalog:detail", kwargs={"slug": self.slug})


class CarSpec(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="specs")
    group = models.CharField("گروه", max_length=60, blank=True, help_text="مثلاً موتور، ابعاد، ایمنی")
    title = models.CharField("مشخصه", max_length=100)
    value = models.CharField("مقدار", max_length=200)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "مشخصه فنی"
        verbose_name_plural = "مشخصات فنی"

    def __str__(self):
        return f"{self.title}: {self.value}"


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("تصویر", upload_to="cars/gallery/")
    caption = models.CharField("توضیح تصویر", max_length=150, blank=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "تصویر گالری"
        verbose_name_plural = "گالری تصاویر"

    def __str__(self):
        return self.caption or f"تصویر {self.pk}"


class CarColor(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="colors")
    name = models.CharField("نام رنگ", max_length=50)
    hex_code = models.CharField(
        "کد رنگ", max_length=7, default="#FFFFFF",
        validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "کد رنگ باید به شکل #RRGGBB باشد.")],
    )

    class Meta:
        verbose_name = "رنگ"
        verbose_name_plural = "رنگ‌های موجود"

    def __str__(self):
        return self.name
