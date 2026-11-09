from django.contrib import admin

from apps.core.admin_utils import image_thumb
from apps.core.templatetags.persian import jdatetime_full

from .models import Part, PartCategory, PartInquiry


@admin.register(PartCategory)
class PartCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order")
    list_editable = ("order",)


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "code", "category", "price", "stock", "is_genuine", "is_active")
    list_display_links = ("thumb", "title")
    list_editable = ("price", "stock", "is_active")
    list_filter = ("category", "stock", "is_genuine", "cars")
    search_fields = ("title", "code")
    filter_horizontal = ("cars",)
    thumb = image_thumb("image", 40)


@admin.register(PartInquiry)
class PartInquiryAdmin(admin.ModelAdmin):
    list_display = ("part_name", "car_model", "full_name", "phone", "status", "created")
    list_editable = ("status",)
    list_filter = ("status",)
    search_fields = ("part_name", "full_name", "phone")
    readonly_fields = ("created",)

    @admin.display(description="تاریخ", ordering="created_at")
    def created(self, obj):
        return jdatetime_full(obj.created_at) if obj.created_at else "—"
