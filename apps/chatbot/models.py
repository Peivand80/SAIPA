from django.db import models


class BotAnswer(models.Model):
    """
    پاسخ‌های آماده چت‌بات. اگر یکی از کلمات کلیدی در پیام کاربر باشد، این پاسخ داده می‌شود.
    پاسخ‌هایی که «دکمه سریع» دارند، به‌صورت دکمه در ابتدای گفتگو نمایش داده می‌شوند.
    """

    title = models.CharField("عنوان / متن دکمه", max_length=80, help_text="مثلاً: ساعات کاری")
    keywords = models.TextField(
        "کلمات کلیدی", help_text="با ویرگول جدا کنید. مثلاً: ساعت, ساعات کاری, باز, تعطیل",
    )
    answer = models.TextField("پاسخ")
    link_url = models.CharField("لینک (اختیاری)", max_length=300, blank=True, help_text="مثلاً /services/appointment/")
    link_label = models.CharField("متن لینک", max_length=60, blank=True)
    is_quick = models.BooleanField("نمایش به‌عنوان دکمه سریع", default=False)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "پاسخ آماده"
        verbose_name_plural = "پاسخ‌های آماده چت‌بات"

    def __str__(self):
        return self.title

    @property
    def keyword_list(self):
        return [k.strip() for k in self.keywords.replace("،", ",").split(",") if k.strip()]


class ChatLog(models.Model):
    """سؤال‌های کاربران؛ برای دیدن سؤال‌های بی‌پاسخ و افزودن پاسخ جدید."""

    question = models.CharField("سؤال کاربر", max_length=500)
    answered = models.BooleanField("پاسخ داده شد", default=False)
    matched = models.CharField("پاسخ استفاده‌شده", max_length=120, blank=True)
    session_key = models.CharField("نشست", max_length=64, blank=True)
    created_at = models.DateTimeField("زمان", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "گفتگوی کاربر"
        verbose_name_plural = "سؤال‌های کاربران"

    def __str__(self):
        return self.question[:60]
