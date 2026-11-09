from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.core.utils import get_client_ip

from .engine import reply
from .models import ChatLog

MAX_MESSAGES = 40      # حداکثر پیام از هر IP
WINDOW_SECONDS = 600   # در هر ۱۰ دقیقه


@require_POST
def ask(request):
    message = (request.POST.get("message") or "").strip()[:500]
    key = f"chatbot:{get_client_ip(request)}"
    count = cache.get(key, 0)
    if count >= MAX_MESSAGES:
        return JsonResponse({"answer": "تعداد پیام‌ها زیاد است. لطفاً چند دقیقه بعد دوباره تلاش کنید."}, status=429)
    cache.set(key, count + 1, WINDOW_SECONDS)

    data, matched = reply(message)
    if message:
        ChatLog.objects.create(
            question=message, answered=bool(matched), matched=matched[:120],
            session_key=request.session.session_key or "",
        )
    data.setdefault("links", [])
    data.setdefault("suggestions", [])
    return JsonResponse(data)
