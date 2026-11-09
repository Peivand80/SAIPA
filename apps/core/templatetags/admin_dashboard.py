from django import template
from django.urls import reverse
from django.utils import timezone

register = template.Library()


@register.inclusion_tag("admin/dashboard_stats.html")
def admin_stats():
    """کارت‌های خلاصه وضعیت در صفحه اول پنل ادمین."""
    from apps.chatbot.models import ChatLog
    from apps.contact.models import ContactMessage
    from apps.interactions.models import Comment
    from apps.parts.models import PartInquiry
    from apps.services.models import Appointment

    today = timezone.localdate()
    cards = [
        {
            "label": "نظرات در انتظار تأیید",
            "value": Comment.objects.filter(is_approved=False).count(),
            "url": reverse("admin:interactions_comment_changelist") + "?is_approved__exact=0",
        },
        {
            "label": "نوبت‌های در انتظار تأیید",
            "value": Appointment.objects.filter(status="pending").count(),
            "url": reverse("admin:services_appointment_changelist") + "?status__exact=pending",
        },
        {
            "label": "نوبت‌های امروز",
            "value": Appointment.objects.filter(date=today).exclude(status="cancelled").count(),
            "url": reverse("admin:services_appointment_changelist")
            + f"?date__day={today.day}&date__month={today.month}&date__year={today.year}",
        },
        {
            "label": "پیام‌های خوانده‌نشده",
            "value": ContactMessage.objects.filter(is_read=False).count(),
            "url": reverse("admin:contact_contactmessage_changelist") + "?is_read__exact=0",
        },
        {
            "label": "استعلام‌های جدید قطعه",
            "value": PartInquiry.objects.filter(status="new").count(),
            "url": reverse("admin:parts_partinquiry_changelist") + "?status__exact=new",
        },
        {
            "label": "سؤال‌های بی‌پاسخ چت‌بات",
            "value": ChatLog.objects.filter(answered=False).count(),
            "url": reverse("admin:chatbot_chatlog_changelist") + "?answered__exact=0",
        },
    ]
    shortcuts = [
        ("نوشتن مطلب جدید", reverse("admin:blog_post_add")),
        ("افزودن خودرو", reverse("admin:catalog_car_add")),
        ("افزودن قطعه", reverse("admin:parts_part_add")),
        ("افزودن ویدیو / ریلز", reverse("admin:core_video_add")),
        ("پاسخ جدید چت‌بات", reverse("admin:chatbot_botanswer_add")),
        ("تنظیمات سایت", reverse("admin:core_sitesettings_changelist")),
        ("مشاهده سایت", "/"),
    ]
    return {"cards": cards, "shortcuts": shortcuts}
