from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.utils import get_client_ip, is_throttled

from .forms import ContactForm


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data.get("website"):
                if is_throttled(request, "contact"):
                    messages.error(request, "تعداد پیام‌های ارسالی شما زیاد است. لطفاً کمی بعد تلاش کنید.")
                    return redirect("contact:contact")
                msg = form.save(commit=False)
                msg.ip_address = get_client_ip(request) or None
                msg.save()
            messages.success(request, "پیام شما با موفقیت ارسال شد. در اسرع وقت پاسخ می‌دهیم.")
            return redirect("contact:contact")
        messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")
    else:
        form = ContactForm(initial={"subject": request.GET.get("subject", "other")})
    return render(request, "contact/contact.html", {"form": form})
