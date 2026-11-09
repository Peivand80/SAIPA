from django.core.cache import cache
from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from .utils import unique_slugify


class TimeStampedModel(models.Model):
    """مدل پایه با زمان ایجاد و ویرایش."""

    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        abstract = True


class SluggedModel(TimeStampedModel):
    """مدل پایه با اسلاگ خودکار (فارسی) از روی فیلد title."""

    slug_source = "title"
    slug = models.SlugField(
        "نامک (اسلاگ)", max_length=200, unique=True, allow_unicode=True, blank=True,
        help_text="بخشی از آدرس صفحه. اگر خالی بماند خودکار ساخته می‌شود.",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, getattr(self, self.slug_source))
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# تنظیمات کلی سایت (فقط یک ردیف)
# ---------------------------------------------------------------------------
class SiteSettings(models.Model):
    CACHE_KEY = "site_settings"

    # هویت
    site_name = models.CharField("نام سایت", max_length=150, default="نمایندگی سایپا - جدیدالاسلامی")
    dealer_code = models.CharField("کد نمایندگی", max_length=30, blank=True)
    slogan = models.CharField("شعار کوتاه", max_length=200, blank=True, default="فروش، خدمات پس از فروش و قطعات اصلی")
    logo = models.ImageField("لوگو", upload_to="site/", blank=True, help_text="ترجیحاً PNG با پس‌زمینه شفاف")
    favicon = models.ImageField("آیکون تب مرورگر", upload_to="site/", blank=True)

    # بخش اصلی صفحه خانه
    hero_title = models.CharField("تیتر اصلی صفحه خانه", max_length=200, default="همراه مطمئن شما در مسیر")
    hero_subtitle = models.TextField(
        "متن زیر تیتر", blank=True,
        default="فروش محصولات سایپا، تعمیرات و سرویس دوره‌ای، قطعات یدکی اصلی و خدمات گارانتی در یک‌جا.",
    )
    hero_image = models.ImageField("تصویر بخش اصلی", upload_to="site/", blank=True)
    hero_button_text = models.CharField("متن دکمه اصلی", max_length=50, default="رزرو نوبت تعمیرگاه")
    hero_button_link = models.CharField("لینک دکمه اصلی", max_length=200, default="/services/appointment/")

    # درباره ما
    about_title = models.CharField("عنوان درباره ما", max_length=150, default="درباره نمایندگی")
    about_summary = models.TextField("خلاصه درباره ما", blank=True, help_text="در صفحه خانه و پاورقی نمایش داده می‌شود.")
    about_body = CKEditor5Field("متن کامل درباره ما", config_name="extends", blank=True)
    about_image = models.ImageField("تصویر درباره ما", upload_to="site/", blank=True)

    # تماس
    phone = models.CharField("تلفن ثابت", max_length=50, blank=True)
    mobile = models.CharField("تلفن همراه", max_length=50, blank=True)
    email = models.EmailField("ایمیل", blank=True)
    address = models.TextField("آدرس", blank=True)
    working_hours = models.TextField("ساعات کاری", blank=True, default="شنبه تا چهارشنبه: ۸ تا ۱۷\nپنجشنبه: ۸ تا ۱۳")
    map_embed_url = models.URLField(
        "لینک نقشه (iframe)", blank=True, max_length=1000,
        help_text="فقط آدرس src کد embed نقشه (نشان، بلد یا گوگل) را وارد کنید.",
    )

    # شبکه‌های اجتماعی
    instagram = models.URLField("اینستاگرام", blank=True)
    telegram = models.URLField("تلگرام", blank=True)
    whatsapp = models.URLField("واتساپ", blank=True)
    eitaa = models.URLField("ایتا", blank=True)
    bale = models.URLField("بله", blank=True)

    # نوبت‌دهی
    appointment_enabled = models.BooleanField("نوبت‌دهی آنلاین فعال است", default=True)
    appointment_days_ahead = models.PositiveSmallIntegerField("تعداد روزهای قابل رزرو", default=14)
    closed_on_friday = models.BooleanField("جمعه‌ها تعطیل است", default=True)
    closed_on_thursday = models.BooleanField("پنجشنبه‌ها تعطیل است", default=False)
    appointment_notice = models.TextField(
        "توضیحات فرم نوبت‌دهی", blank=True,
        default="لطفاً ۱۵ دقیقه قبل از زمان نوبت در پذیرش حضور داشته باشید. نوبت پس از تماس کارشناس قطعی می‌شود.",
    )

    # سئو و پاورقی
    meta_description = models.CharField("توضیحات متا (سئو)", max_length=300, blank=True)
    footer_text = models.CharField("متن کپی‌رایت پاورقی", max_length=200, blank=True)

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return "تنظیمات سایت"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    def delete(self, *args, **kwargs):
        pass  # این ردیف حذف نمی‌شود

    @classmethod
    def load(cls):
        obj = cache.get(cls.CACHE_KEY)
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set(cls.CACHE_KEY, obj, 300)
        return obj

    @property
    def social_links(self):
        items = [
            ("instagram", "اینستاگرام", self.instagram),
            ("telegram", "تلگرام", self.telegram),
            ("whatsapp", "واتساپ", self.whatsapp),
            ("eitaa", "ایتا", self.eitaa),
            ("bale", "بله", self.bale),
        ]
        return [{"key": k, "label": label, "url": url} for k, label, url in items if url]


class HomeStat(models.Model):
    value = models.CharField("عدد", max_length=30, help_text="مثلاً ۲۵+ یا ۱۲٬۰۰۰")
    label = models.CharField("عنوان", max_length=80, help_text="مثلاً سال سابقه")
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "آمار صفحه خانه"
        verbose_name_plural = "آمار صفحه خانه"

    def __str__(self):
        return f"{self.value} {self.label}"


class TeamMember(models.Model):
    name = models.CharField("نام و نام خانوادگی", max_length=120)
    role = models.CharField("سمت", max_length=120)
    photo = models.ImageField("تصویر", upload_to="team/", blank=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("نمایش در سایت", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "عضو تیم"
        verbose_name_plural = "اعضای تیم"

    def __str__(self):
        return f"{self.name} - {self.role}"


class Page(SluggedModel):
    """صفحات ثابت مثل قوانین، حریم خصوصی، شرایط فروش و ..."""

    title = models.CharField("عنوان", max_length=200)
    body = CKEditor5Field("متن صفحه", config_name="extends")
    meta_description = models.CharField("توضیحات متا", max_length=300, blank=True)
    show_in_footer = models.BooleanField("نمایش لینک در پاورقی", default=True)
    is_published = models.BooleanField("منتشر شود", default=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "صفحه ثابت"
        verbose_name_plural = "صفحات ثابت"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:page", kwargs={"slug": self.slug})


class ShowcasePhoto(models.Model):
    """
    تصاویر نمایندگی (سالن فروش، تعمیرگاه، پذیرش و ...).
    در بخش اصلی صفحه خانه به‌صورت ستون‌های متحرک و در گالری «فضای نمایندگی» نمایش داده می‌شوند.
    اگر هیچ تصویری ثبت نشده باشد، تصاویر پیش‌فرض داخل پروژه استفاده می‌شوند.
    """

    image = models.ImageField("تصویر", upload_to="showcase/", help_text="ترجیحاً عمودی (پرتره)")
    caption = models.CharField("عنوان تصویر", max_length=100, blank=True, help_text="مثلاً تعمیرگاه مرکزی")
    order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("نمایش در سایت", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "تصویر نمایندگی"
        verbose_name_plural = "تصاویر نمایندگی (صفحه خانه و گالری)"

    def __str__(self):
        return self.caption or f"تصویر {self.pk}"


class Video(models.Model):
    """
    کلیپ‌ها و ریلزهای نمایندگی. بی‌صدا و خودکار در سایت پخش می‌شوند.
    اگر هیچ ویدیویی ثبت نشده باشد، ویدیوهای پیش‌فرض داخل پروژه نمایش داده می‌شوند.
    """

    class Placement(models.TextChoices):
        REELS = "reels", "بخش ریلزها (عمودی)"
        BAND = "band", "نوار ویدیویی تمام‌عرض (افقی)"

    title = models.CharField("عنوان", max_length=120)
    file = models.FileField(
        "فایل ویدیو (MP4)", upload_to="videos/",
        help_text="MP4 با کدک H.264. ویدیو بی‌صدا پخش می‌شود؛ برای سرعت بهتر، حجم زیر ۵ مگابایت پیشنهاد می‌شود.",
    )
    poster = models.ImageField("تصویر پیش‌نمایش", upload_to="videos/posters/", blank=True)
    placement = models.CharField("محل نمایش", max_length=10, choices=Placement.choices, default=Placement.REELS)
    link = models.CharField("لینک (اختیاری)", max_length=300, blank=True, help_text="مثلاً لینک پست اینستاگرام")
    order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("نمایش در سایت", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "ویدیو / ریلز"
        verbose_name_plural = "ویدیوها و ریلزها"

    def __str__(self):
        return self.title
