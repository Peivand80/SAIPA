"""
تصاویر پیش‌فرض داخل پروژه (static/img).
تا وقتی محتوای مشابه از پنل مدیریت ثبت نشده، سایت از این تصاویر استفاده می‌کند.
"""
from django.templatetags.static import static

SHOWCASE_PHOTOS = [
    ("img/site/storefront.jpg", "سالن فروش نمایندگی"),
    ("img/site/workshop-hall.jpg", "سالن پذیرش و تعمیرگاه"),
    ("img/site/workshop-lifts.jpg", "جایگاه‌های سرویس و تعمیر"),
    ("img/site/reception.jpg", "واحد پذیرش و مشاوره"),
]

# نوار متحرک محصولات وقتی هنوز خودرویی در پنل ثبت نشده
CAR_STRIP = [
    ("img/cars/aria-side.jpg", "آریا"),
    ("img/cars/shahin-blue.jpg", "شاهین"),
    ("img/cars/changan-cs55.jpg", "چانگان CS55 Plus"),
    ("img/cars/crossover-white.jpg", ""),
    ("img/cars/aria-quick.jpg", "آریا و کوییک"),
    ("img/cars/citroen-c3.jpg", "سیتروئن C3-XR"),
    ("img/cars/sedan-gray.jpg", ""),
]

PAGE_HEAD_IMAGES = {
    "catalog": "img/site/storefront.jpg",
    "services": "img/site/workshop-lifts.jpg",
    "parts": "img/site/workshop-hall.jpg",
    "warranty": "img/site/reception.jpg",
    "blog": "img/site/workshop-hall.jpg",
    "contact": "img/site/storefront.jpg",
    "about": "img/site/reception.jpg",
    "default": "img/site/workshop-lifts.jpg",
}


def showcase_photos(queryset):
    """لیست تصاویر نمایندگی: از پنل مدیریت، یا پیش‌فرض‌ها."""
    items = [{"url": p.image.url, "caption": p.caption} for p in queryset if p.image]
    if items:
        return items
    return [{"url": static(path), "caption": caption} for path, caption in SHOWCASE_PHOTOS]


def car_strip(cars):
    """آیتم‌های نوار متحرک محصولات: خودروهای ثبت‌شده، یا تصاویر پیش‌فرض."""
    items = [
        {"url": c.image.url, "title": c.title, "link": c.get_absolute_url(), "tag": c.category.title if c.category else ""}
        for c in cars if c.image
    ]
    if items:
        return items
    return [{"url": static(path), "title": title, "link": "", "tag": ""} for path, title in CAR_STRIP]


ABOUT_IMAGE = "img/site/saipa-banner.jpg"

# ویدیوهای پیش‌فرض (static/video) — (فایل، تصویر پیش‌نمایش، عنوان)
REELS = [
    ("video/reel-jadidoleslami.mp4", "video/reel-jadidoleslami.jpg", "سایپا جدیدالاسلامی"),
    ("video/reel-zamyad-cash-sale.mp4", "video/reel-zamyad-cash-sale.jpg", "فروش نقدی محصولات زامیاد"),
]
BAND_VIDEO = ("video/dealership-clip.mp4", "video/dealership-clip.jpg", "نمایندگی سایپا جدیدالاسلامی")


def videos(queryset):
    """ریلزهای عمودی و ویدیوی نوار تمام‌عرض: از پنل مدیریت، یا پیش‌فرض‌ها."""
    reels, band = [], None
    for v in queryset:
        item = {"url": v.file.url, "poster": v.poster.url if v.poster else "", "title": v.title, "link": v.link}
        if v.placement == "band":
            band = band or item
        else:
            reels.append(item)
    if not reels:
        reels = [{"url": static(f), "poster": static(p), "title": t, "link": ""} for f, p, t in REELS]
    if band is None:
        f, p, t = BAND_VIDEO
        band = {"url": static(f), "poster": static(p), "title": t, "link": ""}
    return reels, band
