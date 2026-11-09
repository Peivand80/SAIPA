from django.contrib import admin

from apps.core.templatetags.persian import jdatetime_full

from .models import BotAnswer, ChatLog


@admin.register(BotAnswer)
class BotAnswerAdmin(admin.ModelAdmin):
    list_display = ("title", "short_answer", "is_quick", "order", "is_active")
    list_editable = ("is_quick", "order", "is_active")
    search_fields = ("title", "keywords", "answer")
    fieldsets = (
        (None, {"fields": ("title", "keywords", "answer")}),
        ("لینک زیر پاسخ", {"fields": ("link_url", "link_label")}),
        ("نمایش", {"fields": ("is_quick", "order", "is_active")}),
    )

    @admin.display(description="پاسخ")
    def short_answer(self, obj):
        return obj.answer[:70] + ("…" if len(obj.answer) > 70 else "")


@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ("question", "answered", "matched", "created")
    list_filter = ("answered",)
    search_fields = ("question",)
    readonly_fields = ("question", "answered", "matched", "session_key", "created")
    exclude = ("created_at",)

    @admin.display(description="زمان", ordering="created_at")
    def created(self, obj):
        return jdatetime_full(obj.created_at)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
