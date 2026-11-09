from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .admin_utils import image_thumb
from .models import HomeStat, Page, ShowcasePhoto, SiteSettings, TeamMember, Video


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("هویت سایت", {"fields": ("site_name", "dealer_code", "slogan", "logo", "favicon")}),
        ("بخش اصلی صفحه خانه", {"fields": ("hero_title", "hero_subtitle", "hero_image", "hero_button_text", "hero_button_link")}),
        ("درباره ما", {"fields": ("about_title", "about_summary", "about_body", "about_image")}),
        ("اطلاعات تماس", {"fields": ("phone", "mobile", "email", "address", "working_hours", "map_embed_url")}),
        ("شبکه‌های اجتماعی", {"fields": ("instagram", "telegram", "whatsapp", "eitaa", "bale"), "classes": ("collapse",)}),
        ("نوبت‌دهی آنلاین", {"fields": ("appointment_enabled", "appointment_days_ahead", "closed_on_friday", "closed_on_thursday", "appointment_notice")}),
        ("سئو و پاورقی", {"fields": ("meta_description", "footer_text"), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # مستقیم به صفحه ویرایش تنها ردیف تنظیمات برو
        obj = SiteSettings.load()
        return redirect(reverse("admin:core_sitesettings_change", args=[obj.pk]))


@admin.register(HomeStat)
class HomeStatAdmin(admin.ModelAdmin):
    list_display = ("value", "label", "order")
    list_editable = ("order",)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("thumb", "name", "role", "order", "is_active")
    list_display_links = ("thumb", "name")
    list_editable = ("order", "is_active")
    thumb = image_thumb("photo", 40)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "show_in_footer", "is_published", "order")
    list_editable = ("show_in_footer", "is_published", "order")
    search_fields = ("title",)


@admin.register(ShowcasePhoto)
class ShowcasePhotoAdmin(admin.ModelAdmin):
    list_display = ("thumb", "caption", "order", "is_active")
    list_display_links = ("thumb", "caption")
    list_editable = ("order", "is_active")
    thumb = image_thumb("image", 60)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "placement", "order", "is_active")
    list_display_links = ("thumb", "title")
    list_editable = ("placement", "order", "is_active")
    list_filter = ("placement", "is_active")
    thumb = image_thumb("poster", 60)
