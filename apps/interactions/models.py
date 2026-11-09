from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class CommentQuerySet(models.QuerySet):
    def approved(self):
        return self.filter(is_approved=True)

    def pending(self):
        return self.filter(is_approved=False)


class Comment(models.Model):
    """
    نظر کاربران (مهمان) روی هر محتوایی (مطلب، خودرو، خدمت).
    نظرات تا زمان تأیید ادمین در سایت نمایش داده نمی‌شوند.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="نوع محتوا")
    object_id = models.PositiveBigIntegerField("شناسه محتوا")
    content_object = GenericForeignKey("content_type", "object_id")

    name = models.CharField("نام", max_length=80)
    email = models.EmailField("ایمیل", blank=True, help_text="نمایش داده نمی‌شود")
    body = models.TextField("متن نظر", max_length=1500)
    is_approved = models.BooleanField("تأیید شده", default=False, db_index=True)
    admin_reply = models.TextField("پاسخ نمایندگی", blank=True, help_text="زیر نظر کاربر نمایش داده می‌شود.")
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    objects = CommentQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        indexes = [models.Index(fields=["content_type", "object_id", "is_approved"])]

    def __str__(self):
        return f"{self.name}: {self.body[:40]}"


class Like(models.Model):
    """هر بازدیدکننده (بر اساس نشست مرورگر) می‌تواند یک بار هر محتوا را لایک کند."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="نوع محتوا")
    object_id = models.PositiveBigIntegerField("شناسه محتوا")
    content_object = GenericForeignKey("content_type", "object_id")
    session_key = models.CharField("نشست", max_length=64)
    created_at = models.DateTimeField("تاریخ", auto_now_add=True)

    class Meta:
        verbose_name = "لایک"
        verbose_name_plural = "لایک‌ها"
        constraints = [
            models.UniqueConstraint(fields=["content_type", "object_id", "session_key"], name="unique_like_per_session")
        ]
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return f"لایک {self.content_type} #{self.object_id}"
