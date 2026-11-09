"""
موتور ساده چت‌بات نمایندگی (بدون هوش مصنوعی و بدون سرویس خارجی).

ترتیب پاسخ‌دهی:
  ۱. پاسخ‌های آماده‌ای که مدیر در پنل تعریف کرده (BotAnswer)
  ۲. پاسخ‌های داخلی که از اطلاعات سایت ساخته می‌شوند (تلفن، آدرس، ساعات کاری، نوبت، محصولات، ...)
  ۳. جستجو در پرسش‌های متداول گارانتی
  ۴. پاسخ پیش‌فرض با راهنمای تماس
"""
import re

from django.urls import reverse

from apps.catalog.models import Car
from apps.core.models import SiteSettings
from apps.core.utils import to_persian_digits

from .models import BotAnswer

ARABIC_MAP = str.maketrans({"ي": "ی", "ك": "ک", "ة": "ه", "أ": "ا", "إ": "ا", "ۀ": "ه", "‌": " "})
DIACRITICS = re.compile(r"[ً-ْٰ]")
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

QUICK_REPLIES = ["رزرو نوبت", "ساعات کاری", "آدرس و تلفن", "محصولات و قیمت", "قطعات یدکی", "گارانتی"]


def normalize(text: str) -> str:
    text = DIACRITICS.sub("", str(text)).translate(ARABIC_MAP).translate(DIGITS).lower()
    text = re.sub(r"[؟?!،,.:;«»\"'()\[\]{}\-_/]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def score(text: str, keywords) -> int:
    """امتیاز تطابق: مجموع طول کلمات کلیدی که در متن آمده‌اند (کلمات بلندتر دقیق‌ترند)."""
    return sum(len(k) for k in (normalize(k) for k in keywords) if k and k in text)


GENERIC_WORDS = {"پلاس", "سایپا", "plus", "جدید", "اتوماتیک", "دنده ای"}


def car_tokens(title: str):
    """بخش‌های شاخص نام خودرو برای تشخیص در پیام (مثلاً «cs55» از «چانگان CS55 پلاس»)."""
    norm = normalize(title)
    tokens = {norm}
    for t in norm.split():
        if t in GENERIC_WORDS:
            continue
        if len(t) >= 3 or any(ch.isdigit() for ch in t):
            tokens.add(t)
    return tokens


def mentions(text: str, title: str) -> bool:
    words = set(text.split())
    return any((tok in words) if " " not in tok else (tok in text) for tok in car_tokens(title))


def link(url_name, label, **kwargs):
    return {"url": reverse(url_name, kwargs=kwargs or None), "label": label}


# ---------------------------------------------------------------------------
# پاسخ‌های داخلی
# ---------------------------------------------------------------------------
def _contact(site):
    lines = []
    if site.phone:
        lines.append(f"تلفن: {to_persian_digits(site.phone)}")
    if site.mobile:
        lines.append(f"همراه: {to_persian_digits(site.mobile)}")
    return lines


def intent_greeting(site, text):
    return {"answer": f"سلام، به {site.site_name} خوش آمدید. چطور می‌توانم کمکتان کنم؟ می‌توانید سؤالتان را بنویسید یا یکی از گزینه‌های زیر را انتخاب کنید."}


def intent_thanks(site, text):
    return {"answer": "خواهش می‌کنم. اگر سؤال دیگری دارید، در خدمتم."}


def intent_hours(site, text):
    hours = to_persian_digits(site.working_hours) if site.working_hours else "ساعات کاری هنوز در سایت ثبت نشده است."
    return {"answer": f"ساعات کاری نمایندگی:\n{hours}", "links": [link("contact:contact", "اطلاعات تماس")]}


def intent_contact(site, text):
    lines = _contact(site)
    if site.address:
        lines.append(f"آدرس: {to_persian_digits(site.address)}")
    if not lines:
        lines = ["اطلاعات تماس به‌زودی در سایت قرار می‌گیرد. فعلاً می‌توانید از فرم تماس پیام بفرستید."]
    return {"answer": "\n".join(lines), "links": [link("contact:contact", "صفحه تماس با ما")]}


def intent_address(site, text):
    if site.address:
        answer = f"آدرس نمایندگی:\n{to_persian_digits(site.address)}"
        if site.working_hours:
            answer += f"\n\nساعات کاری:\n{to_persian_digits(site.working_hours)}"
    else:
        answer = "آدرس نمایندگی به‌زودی در سایت ثبت می‌شود."
    return {"answer": answer, "links": [link("contact:contact", "مشاهده روی نقشه")]}


def intent_track(site, text):
    return {
        "answer": "برای دیدن وضعیت نوبت، کد پیگیری ۸ رقمی و شماره موبایلی را که هنگام رزرو وارد کردید در صفحه پیگیری بنویسید.",
        "links": [link("services:track", "پیگیری نوبت")],
    }


def intent_appointment(site, text):
    if not site.appointment_enabled:
        return {"answer": "نوبت‌دهی آنلاین فعلاً غیرفعال است. لطفاً برای رزرو نوبت با پذیرش تماس بگیرید.\n" + "\n".join(_contact(site))}
    return {
        "answer": (
            "نوبت تعمیرگاه را می‌توانید آنلاین رزرو کنید: نوع خدمت، روز و ساعت مراجعه را انتخاب کنید و "
            f"کد پیگیری بگیرید. نوبت‌ها تا {to_persian_digits(site.appointment_days_ahead)} روز آینده قابل رزرو هستند."
        ),
        "links": [link("services:appointment", "رزرو نوبت"), link("services:track", "پیگیری نوبت")],
    }


def intent_products(site, text):
    cars = list(Car.objects.active().only("title", "slug", "price_text", "summary")[:20])
    # اگر نام یک خودرو در پیام آمده باشد، همان را معرفی کن
    for car in cars:
        if mentions(text, car.title):
            answer = f"{car.title}: {car.summary}"
            if car.price_text:
                answer += f"\n\nقیمت / وضعیت فروش: {car.price_text}"
            return {"answer": answer, "links": [{"url": car.get_absolute_url(), "label": f"مشخصات کامل {car.title}"},
                                                link("contact:contact", "مشاوره خرید")]}
    if not cars:
        return {"answer": "فهرست محصولات به‌زودی در سایت قرار می‌گیرد. برای اطلاع از شرایط فروش با واحد فروش تماس بگیرید.",
                "links": [link("contact:contact", "تماس با واحد فروش")]}
    names = "، ".join(c.title for c in cars)
    return {
        "answer": f"محصولاتی که در سایت معرفی شده‌اند: {names}.\nقیمت‌ها طبق آخرین بخشنامه فروش سایپا اعلام می‌شود. نام خودروی مورد نظرتان را بنویسید تا مشخصاتش را بفرستم.",
        "links": [link("catalog:list", "همه محصولات")],
        "suggestions": [c.title for c in cars[:4]],
    }


def intent_parts(site, text):
    return {
        "answer": "قطعات یدکی اصلی را در صفحه قطعات می‌توانید بر اساس نام، کد فنی یا مدل خودرو جستجو کنید. اگر قطعه‌ای را پیدا نکردید، فرم استعلام را پر کنید تا کارشناس قطعات با شما تماس بگیرد.",
        "links": [link("parts:list", "جستجوی قطعات"), link("parts:inquiry", "استعلام قطعه")],
    }


def intent_warranty(site, text):
    from apps.warranty.models import FAQ

    best, best_score = None, 0
    words = [w for w in text.split() if len(w) > 2]
    for faq in FAQ.objects.filter(is_active=True)[:100]:
        q = normalize(faq.question)
        s = sum(len(w) for w in words if w in q)
        if s > best_score:
            best, best_score = faq, s
    if best and best_score >= 6:
        return {"answer": f"{best.question}\n{best.answer}", "links": [link("warranty:index", "گارانتی و کارت طلایی")]}
    return {
        "answer": "شرایط گارانتی، کارت طلایی، مدارک لازم و پرسش‌های متداول در صفحه گارانتی آمده است. اگر سؤال مشخصی دارید، آن را بنویسید.",
        "links": [link("warranty:index", "گارانتی و کارت طلایی")],
    }


def intent_services(site, text):
    return {
        "answer": "خدمات پس از فروش نمایندگی شامل سرویس دوره‌ای، تعمیرات مکانیکی، برق خودرو، صافکاری و نقاشی و عیب‌یابی است.",
        "links": [link("services:list", "همه خدمات"), link("services:appointment", "رزرو نوبت")],
    }


# (کلمات کلیدی، تابع پاسخ) — ترتیب مهم است: اولی در امتیاز برابر برنده است
INTENTS = [
    (["پیگیری نوبت", "کد پیگیری", "وضعیت نوبت", "پیگیری"], intent_track),
    (["نوبت سرویس", "نوبت تعمیر", "نوبت", "رزرو", "وقت بگیرم", "پذیرش"], intent_appointment),
    (["ساعات کاری", "ساعت کاری", "ساعت", "باز است", "بازه", "تعطیل", "چه ساعتی"], intent_hours),
    (["آدرس", "نشانی", "کجاست", "کجا", "مسیر", "لوکیشن", "نقشه"], intent_address),
    (["آدرس و تلفن", "تلفن", "شماره", "تماس", "زنگ", "موبایل"], intent_contact),
    (["محصولات و قیمت", "محصول", "خودرو", "ماشین", "قیمت", "فروش", "خرید", "بخشنامه", "ثبت نام", "پیش فروش"], intent_products),
    (["قطعات یدکی", "قطعه", "قطعات", "لوازم", "یدکی"], intent_parts),
    (["کارت طلایی", "گارانتی", "ضمانت", "وارانتی"], intent_warranty),
    (["خدمات", "تعمیر", "سرویس", "تعویض روغن", "صافکاری", "نقاشی", "برق خودرو"], intent_services),
    (["سلام", "درود", "وقت بخیر", "روز بخیر", "hi", "hello"], intent_greeting),
    (["ممنون", "مرسی", "تشکر", "سپاس", "متشکرم"], intent_thanks),
]


def fallback(site):
    contact = _contact(site)
    answer = "متوجه سؤالتان نشدم. لطفاً کوتاه‌تر بنویسید یا یکی از گزینه‌ها را انتخاب کنید."
    if contact:
        answer += "\nبرای پاسخ دقیق‌تر می‌توانید تماس بگیرید:\n" + "\n".join(contact)
    return {"answer": answer, "links": [link("contact:contact", "ارسال پیام برای کارشناس")], "suggestions": QUICK_REPLIES}


def reply(message: str) -> tuple[dict, str]:
    """پاسخ به پیام کاربر. خروجی: (پاسخ، نام پاسخ استفاده‌شده یا رشته خالی)"""
    site = SiteSettings.load()
    text = normalize(message)
    if not text:
        return intent_greeting(site, text), "greeting"

    # ۱. پاسخ‌های آماده مدیر (با اولویت در امتیاز برابر)
    best_custom, best_custom_score = None, 0
    for ans in BotAnswer.objects.filter(is_active=True):
        s = score(text, ans.keyword_list + [ans.title])
        if s > best_custom_score:
            best_custom, best_custom_score = ans, s

    # ۲. پاسخ‌های داخلی
    best_intent, best_intent_score = None, 0
    for keywords, func in INTENTS:
        s = score(text, keywords)
        if s > best_intent_score:
            best_intent, best_intent_score = func, s

    # نام خودروها هم نشانه سؤال درباره محصولات است
    for title in Car.objects.active().values_list("title", flat=True)[:30]:
        if mentions(text, title) and 5 > best_intent_score:
            best_intent, best_intent_score = intent_products, 5

    if best_custom and best_custom_score >= best_intent_score:
        data = {"answer": best_custom.answer}
        if best_custom.link_url:
            data["links"] = [{"url": best_custom.link_url, "label": best_custom.link_label or "مشاهده"}]
        return data, best_custom.title
    if best_intent:
        return best_intent(site, text), best_intent.__name__.replace("intent_", "")
    return fallback(site), ""


def quick_replies():
    custom = list(BotAnswer.objects.filter(is_active=True, is_quick=True).values_list("title", flat=True)[:4])
    return QUICK_REPLIES + [c for c in custom if c not in QUICK_REPLIES]


def greeting_text():
    site = SiteSettings.load()
    return f"سلام! من دستیار {site.site_name} هستم. درباره نوبت تعمیرگاه، محصولات، قطعات، گارانتی، آدرس و ساعات کاری می‌توانم راهنمایی‌تان کنم."

