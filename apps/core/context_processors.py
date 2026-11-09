from django.templatetags.static import static

from .defaults import PAGE_HEAD_IMAGES
from .models import Page, SiteSettings

NAV_ITEMS = [
    ("core:home", "خانه", "core"),
    ("catalog:list", "محصولات", "catalog"),
    ("services:list", "خدمات", "services"),
    ("parts:list", "قطعات یدکی", "parts"),
    ("warranty:index", "گارانتی و کارت طلایی", "warranty"),
    ("blog:list", "مجله", "blog"),
    ("core:about", "درباره ما", "about"),
    ("contact:contact", "تماس با ما", "contact"),
]


def site_context(request):
    """اطلاعاتی که در همه قالب‌ها در دسترس است."""
    match = getattr(request, "resolver_match", None)
    namespace = match.namespace if match else ""
    url_name = match.url_name if match else ""
    current = "about" if url_name == "about" else namespace
    if namespace == "core" and url_name != "home":
        current = "about" if url_name == "about" else ""

    return {
        "site": SiteSettings.load(),
        "footer_pages": Page.objects.filter(is_published=True, show_in_footer=True).only("title", "slug"),
        "page_head_image": static(PAGE_HEAD_IMAGES.get(current or namespace, PAGE_HEAD_IMAGES["default"])),
        "nav_items": [
            {"url_name": u, "label": label, "active": key == current} for u, label, key in NAV_ITEMS
        ],
    }
