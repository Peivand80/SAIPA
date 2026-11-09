from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html

from apps.core.templatetags.persian import jdatetime_full

from .models import Comment, Like


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "short_body", "target_link", "is_approved", "has_reply", "created_jalali")
    list_display_links = ("name", "short_body")
    list_editable = ("is_approved",)
    list_filter = ("is_approved", "content_type", "created_at")
    search_fields = ("name", "email", "body")
    readonly_fields = ("content_type", "object_id", "target_link", "ip_address", "created_jalali")
    fieldsets = (
        ("نظر کاربر", {"fields": ("name", "email", "body", "target_link", "created_jalali", "ip_address")}),
        ("بررسی و پاسخ", {"fields": ("is_approved", "admin_reply")}),
    )
    actions = ("approve", "unapprove")
    list_per_page = 30

    @admin.display(description="متن نظر")
    def short_body(self, obj):
        return obj.body[:70] + ("…" if len(obj.body) > 70 else "")

    @admin.display(description="مربوط به")
    def target_link(self, obj):
        target = obj.content_object
        if target is None:
            return "—"
        url = getattr(target, "get_absolute_url", lambda: "")()
        return format_html('<a href="{}" target="_blank">{}</a>', url, target) if url else str(target)

    @admin.display(description="پاسخ", boolean=True)
    def has_reply(self, obj):
        return bool(obj.admin_reply)

    @admin.display(description="تاریخ ثبت", ordering="created_at")
    def created_jalali(self, obj):
        return jdatetime_full(obj.created_at)

    @admin.action(description="تأیید نظرات انتخاب‌شده")
    def approve(self, request, queryset):
        n = queryset.update(is_approved=True)
        self.message_user(request, f"{n} نظر تأیید شد.", messages.SUCCESS)

    @admin.action(description="لغو تأیید نظرات انتخاب‌شده")
    def unapprove(self, request, queryset):
        n = queryset.update(is_approved=False)
        self.message_user(request, f"تأیید {n} نظر لغو شد.", messages.WARNING)

    def has_add_permission(self, request):
        return False


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("content_type", "object_id", "created_at")
    list_filter = ("content_type",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class CommentInline(GenericTabularInline):
    """نمایش و تأیید نظرات داخل صفحه ویرایش مطلب / خودرو / خدمت."""

    model = Comment
    extra = 0
    fields = ("name", "body", "is_approved", "admin_reply")
    readonly_fields = ("name", "body")
    verbose_name_plural = "نظرات این محتوا"
    classes = ("collapse",)

    def has_add_permission(self, request, obj=None):
        return False
