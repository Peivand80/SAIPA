from django.contrib import admin

from apps.core.admin_utils import image_thumb
from apps.interactions.admin import CommentInline

from .models import Car, CarCategory, CarColor, CarImage, CarSpec


@admin.register(CarCategory)
class CarCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order")
    list_editable = ("order",)


class CarSpecInline(admin.TabularInline):
    model = CarSpec
    extra = 3
    fields = ("group", "title", "value", "order")


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1
    fields = ("thumb", "image", "caption", "order")
    readonly_fields = ("thumb",)
    thumb = image_thumb("image", 50)


class CarColorInline(admin.TabularInline):
    model = CarColor
    extra = 1


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "category", "price_text", "is_featured", "is_active", "order")
    list_display_links = ("thumb", "title")
    list_editable = ("is_featured", "is_active", "order")
    list_filter = ("category", "is_active", "is_featured")
    search_fields = ("title", "summary")
    readonly_fields = ("thumb_large",)
    inlines = [CarSpecInline, CarImageInline, CarColorInline, CommentInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "tagline", "summary")}),
        ("تصویر", {"fields": ("image", "thumb_large")}),
        ("معرفی کامل", {"fields": ("description",)}),
        ("فروش", {"fields": ("price_text", "sale_link", "brochure")}),
        ("نمایش", {"fields": ("is_featured", "is_active", "order")}),
    )
    thumb = image_thumb("image", 40)
    thumb_large = image_thumb("image", 140, "پیش‌نمایش")
