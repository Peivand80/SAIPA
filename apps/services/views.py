import datetime

from django.conf import settings
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

from apps.core.models import SiteSettings
from apps.core.utils import get_client_ip, is_throttled
from apps.interactions.mixins import CommentableMixin

from .booking import available_dates, slot_availability
from .forms import AppointmentForm, TrackForm
from .models import Appointment, Service


class ServiceListView(ListView):
    template_name = "services/service_list.html"
    context_object_name = "services"
    paginate_by = settings.PAGINATION["services"]

    def get_queryset(self):
        return Service.objects.active()


class ServiceDetailView(CommentableMixin, DetailView):
    template_name = "services/service_detail.html"
    context_object_name = "service"

    def get_queryset(self):
        return Service.objects.active()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["other_services"] = Service.objects.active().exclude(pk=self.object.pk)[:5]
        return context


def appointment(request):
    site = SiteSettings.load()
    if not site.appointment_enabled:
        return render(request, "services/appointment_closed.html")

    initial = {}
    if request.GET.get("service"):
        initial["service"] = Service.objects.filter(slug=request.GET["service"]).first()

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("website"):
                return redirect("services:appointment")
            if is_throttled(request, "appointment"):
                messages.error(request, "تعداد درخواست‌های شما زیاد است. لطفاً کمی بعد تلاش کنید یا تماس بگیرید.")
                return redirect("services:appointment")
            obj = form.save(commit=False)
            obj.ip_address = get_client_ip(request) or None
            obj.save()
            request.session["last_appointment"] = obj.pk
            return redirect("services:appointment_done")
        messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")
    else:
        form = AppointmentForm(initial=initial)

    return render(request, "services/appointment_form.html", {"form": form})


def appointment_done(request):
    pk = request.session.get("last_appointment")
    obj = Appointment.objects.filter(pk=pk).select_related("service", "slot").first() if pk else None
    if not obj:
        return redirect("services:appointment")
    return render(request, "services/appointment_done.html", {"appointment": obj})


def availability(request):
    """API کوچک برای به‌روزرسانی ساعت‌های آزاد پس از انتخاب روز در فرم."""
    try:
        day = datetime.date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        raise Http404
    if day not in available_dates():
        return JsonResponse({"slots": []})
    slots = [
        {"id": s["id"], "label": s["label"], "remaining": s["remaining"], "available": s["available"]}
        for s in slot_availability(day)
    ]
    return JsonResponse({"slots": slots})


def track(request):
    appointment_obj = None
    searched = False
    form = TrackForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        searched = True
        appointment_obj = (
            Appointment.objects.select_related("service", "slot")
            .filter(tracking_code=form.cleaned_data["code"], phone=form.cleaned_data["phone"])
            .first()
        )
    return render(
        request, "services/appointment_track.html",
        {"form": form, "appointment": appointment_obj, "searched": searched},
    )
