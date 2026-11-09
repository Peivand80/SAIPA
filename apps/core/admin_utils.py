from django.contrib import admin
from django.utils.html import format_html


def image_thumb(field_name, size=60, description="تصویر"):
    """یک ستون پیش‌نمایش تصویر برای list_display / readonly_fields می‌سازد."""

    @admin.display(description=description)
    def _thumb(self, obj):
        img = getattr(obj, field_name, None)
        if img:
            return format_html(
                '<img src="{}" style="height:{}px;width:auto;max-width:{}px;border-radius:6px;object-fit:cover">',
                img.url, size, size * 2,
            )
        return "—"

    return _thumb
