from django.contrib import admin

from apps.core.admin_utils import image_thumb
from apps.core.templatetags.persian import jdatetime_full
from apps.interactions.admin import CommentInline

from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order")
    list_editable = ("order",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "category", "status", "is_featured", "published", "views")
    list_display_links = ("thumb", "title")
    list_editable = ("status", "is_featured")
    list_filter = ("status", "category", "is_featured")
    search_fields = ("title", "summary", "body")
    readonly_fields = ("cover_preview", "views")
    date_hierarchy = "published_at"
    inlines = [CommentInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "summary")}),
        ("تصویر شاخص", {"fields": ("cover", "cover_preview")}),
        ("متن مطلب", {"fields": ("body",)}),
        ("انتشار", {"fields": ("status", "published_at", "is_featured", "allow_comments", "views")}),
        ("سئو", {"fields": ("meta_description",), "classes": ("collapse",)}),
    )
    thumb = image_thumb("cover", 40)
    cover_preview = image_thumb("cover", 140, "پیش‌نمایش")

    @admin.display(description="زمان انتشار", ordering="published_at")
    def published(self, obj):
        return jdatetime_full(obj.published_at)

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
