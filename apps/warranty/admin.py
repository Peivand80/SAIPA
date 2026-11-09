from django.contrib import admin

from .models import FAQ, WarrantyPlan


class FAQInline(admin.StackedInline):
    model = FAQ
    extra = 1
    fields = ("question", "answer", "order", "is_active")


@admin.register(WarrantyPlan)
class WarrantyPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order", "is_active")
    list_editable = ("order", "is_active")
    inlines = [FAQInline]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "plan", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("plan", "is_active")
    search_fields = ("question", "answer")
