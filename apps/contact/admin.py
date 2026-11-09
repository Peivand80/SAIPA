from django.contrib import admin, messages

from apps.core.templatetags.persian import jdatetime_full

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "subject", "short_message", "is_read", "created")
    list_editable = ("is_read",)
    list_filter = ("is_read", "subject")
    search_fields = ("full_name", "phone", "email", "message")
    readonly_fields = ("full_name", "phone", "email", "subject", "message", "created", "ip_address")
    fields = ("full_name", "phone", "email", "subject", "message", "created", "is_read", "admin_note", "ip_address")
    actions = ("mark_read",)

    @admin.display(description="پیام")
    def short_message(self, obj):
        return obj.message[:60] + ("…" if len(obj.message) > 60 else "")

    @admin.display(description="تاریخ", ordering="created_at")
    def created(self, obj):
        return jdatetime_full(obj.created_at) if obj.created_at else "—"

    @admin.action(description="علامت‌گذاری به‌عنوان خوانده‌شده")
    def mark_read(self, request, queryset):
        n = queryset.update(is_read=True)
        self.message_user(request, f"{n} پیام خوانده‌شده علامت خورد.", messages.SUCCESS)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        ContactMessage.objects.filter(pk=object_id, is_read=False).update(is_read=True)
        return super().change_view(request, object_id, form_url, extra_context)

    def has_add_permission(self, request):
        return False
