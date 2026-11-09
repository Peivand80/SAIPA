from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from apps.catalog.models import Car
from apps.core.utils import is_throttled

from .forms import PartInquiryForm
from .models import Part, PartCategory


class PartListView(ListView):
    template_name = "parts/part_list.html"
    context_object_name = "parts"
    paginate_by = settings.PAGINATION["parts"]

    def get_queryset(self):
        qs = Part.objects.filter(is_active=True).select_related("category")
        g = self.request.GET
        self.filters = {"q": g.get("q", "").strip(), "category": g.get("category", ""), "car": g.get("car", "")}
        if self.filters["q"]:
            qs = qs.filter(Q(title__icontains=self.filters["q"]) | Q(code__icontains=self.filters["q"]))
        if self.filters["category"]:
            qs = qs.filter(category__slug=self.filters["category"])
        if self.filters["car"]:
            qs = qs.filter(cars__slug=self.filters["car"])
        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "categories": PartCategory.objects.all(),
            "cars": Car.objects.active().only("title", "slug"),
            "filters": self.filters,
        })
        return context


def _handle_inquiry(request, part=None):
    initial = {"part_name": str(part)} if part else {}
    if request.method == "POST":
        form = PartInquiryForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data.get("website"):
                if is_throttled(request, "inquiry"):
                    messages.error(request, "تعداد درخواست‌های شما زیاد است. لطفاً کمی بعد تلاش کنید.")
                    return None, form
                inquiry = form.save(commit=False)
                inquiry.part = part
                inquiry.save()
            messages.success(request, "درخواست استعلام شما ثبت شد. کارشناس قطعات به‌زودی با شما تماس می‌گیرد.")
            return True, None
        messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")
        return None, form
    return None, PartInquiryForm(initial=initial)


def part_detail(request, slug):
    part = get_object_or_404(Part.objects.select_related("category").prefetch_related("cars"), slug=slug, is_active=True)
    done, form = _handle_inquiry(request, part)
    if done:
        return redirect(part.get_absolute_url())
    related = Part.objects.filter(is_active=True, category=part.category).exclude(pk=part.pk)[:4] if part.category else []
    return render(request, "parts/part_detail.html", {
        "part": part, "form": form, "related": related,
        "car_models": Car.objects.active().values_list("title", flat=True),
    })


def inquiry(request):
    done, form = _handle_inquiry(request)
    if done:
        return redirect("parts:inquiry")
    return render(request, "parts/inquiry.html", {
        "form": form, "car_models": Car.objects.active().values_list("title", flat=True),
    })
