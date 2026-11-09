from django.contrib import admin, messages
from django.utils.html import format_html

from apps.core.admin_utils import image_thumb
from apps.core.templatetags.persian import jdate, jdatetime_full, weekday_fa
from apps.interactions.admin import CommentInline

from .models import Appointment, AppointmentSlot, ClosedDay, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "icon", "bookable", "is_active", "order")
    list_display_links = ("thumb", "title")
    list_editable = ("bookable", "is_active", "order")
    search_fields = ("title",)
    inlines = [CommentInline]
    thumb = image_thumb("image", 40)


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ("__str__", "start_time", "end_time", "capacity", "is_active")
    list_editable = ("capacity", "is_active")


@admin.register(ClosedDay)
class ClosedDayAdmin(admin.ModelAdmin):
    list_display = ("jalali", "date", "reason")

    @admin.display(description="تاریخ شمسی", ordering="date")
    def jalali(self, obj):
        return f"{weekday_fa(obj.date)} {jdate(obj.date)}"


STATUS_COLORS = {
    "pending": "#B45309",
    "confirmed": "#1D4ED8",
    "done": "#15803D",
    "cancelled": "#6B7280",
}


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_code", "full_name", "phone", "car_model", "service", "date_jalali", "slot", "status_badge", "status",
    )
    list_display_links = ("tracking_code", "full_name")
    list_editable = ("status",)
    list_filter = ("status", "service", "date", "slot")
    search_fields = ("tracking_code", "full_name", "phone", "plate_number", "car_model")
    date_hierarchy = "date"
    readonly_fields = ("tracking_code", "created_jalali", "ip_address")
    fieldsets = (
        ("مشتری", {"fields": ("tracking_code", "full_name", "phone")}),
        ("خودرو", {"fields": ("car_model", "plate_number", "mileage")}),
        ("نوبت", {"fields": ("service", "date", "slot", "description")}),
        ("پذیرش", {"fields": ("status", "admin_note", "created_jalali", "ip_address")}),
    )
    actions = ("mark_confirmed", "mark_done", "mark_cancelled")
    list_per_page = 30

    @admin.display(description="تاریخ مراجعه", ordering="date")
    def date_jalali(self, obj):
        return f"{weekday_fa(obj.date)} {jdate(obj.date, '%Y/%m/%d')}"

    @admin.display(description="وضعیت فعلی")
    def status_badge(self, obj):
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:12px;font-size:11px">{}</span>',
            STATUS_COLORS.get(obj.status, "#666"), obj.get_status_display(),
        )

    @admin.display(description="زمان ثبت")
    def created_jalali(self, obj):
        return jdatetime_full(obj.created_at) if obj.created_at else "—"

    def _set_status(self, request, queryset, status, label):
        n = queryset.update(status=status)
        self.message_user(request, f"وضعیت {n} نوبت به «{label}» تغییر کرد.", messages.SUCCESS)

    @admin.action(description="تأیید نوبت‌های انتخاب‌شده")
    def mark_confirmed(self, request, queryset):
        self._set_status(request, queryset, Appointment.Status.CONFIRMED, "تأیید شده")

    @admin.action(description="علامت‌گذاری به‌عنوان انجام‌شده")
    def mark_done(self, request, queryset):
        self._set_status(request, queryset, Appointment.Status.DONE, "انجام شده")

    @admin.action(description="لغو نوبت‌های انتخاب‌شده")
    def mark_cancelled(self, request, queryset):
        self._set_status(request, queryset, Appointment.Status.CANCELLED, "لغو شده")
