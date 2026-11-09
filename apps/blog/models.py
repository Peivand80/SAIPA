from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

from apps.core.models import SluggedModel


class Category(SluggedModel):
    title = models.CharField("عنوان", max_length=100)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "دسته‌بندی مطلب"
        verbose_name_plural = "دسته‌بندی‌های مطالب"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Post.Status.PUBLISHED, published_at__lte=timezone.now())


class Post(SluggedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PUBLISHED = "published", "منتشر شده"

    title = models.CharField("عنوان", max_length=200)
    category = models.ForeignKey(
        Category, verbose_name="دسته‌بندی", on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )
    cover = models.ImageField("تصویر شاخص", upload_to="blog/%Y/%m/")
    summary = models.TextField("خلاصه", max_length=400, help_text="در لیست مطالب و نتایج جستجو نمایش داده می‌شود.")
    body = CKEditor5Field("متن مطلب", config_name="extends")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="نویسنده", on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField("وضعیت", max_length=10, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(
        "زمان انتشار", default=timezone.now, help_text="می‌توانید زمان آینده بدهید تا خودکار منتشر شود."
    )
    is_featured = models.BooleanField("مطلب ویژه", default=False)
    allow_comments = models.BooleanField("امکان ثبت نظر", default=True)
    views = models.PositiveIntegerField("بازدید", default=0, editable=False)
    meta_description = models.CharField("توضیحات متا (سئو)", max_length=300, blank=True)

    comments = GenericRelation("interactions.Comment")
    likes = GenericRelation("interactions.Like")

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "مطلب"
        verbose_name_plural = "مطالب"
        indexes = [models.Index(fields=["status", "published_at"])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    @property
    def reading_time(self):
        import re

        words = len(re.sub(r"<[^>]+>", " ", self.body or "").split())
        return max(1, round(words / 200))
