from django.shortcuts import get_object_or_404, render

from .models import FAQ, WarrantyPlan


def index(request):
    return render(request, "warranty/index.html", {
        "plans": WarrantyPlan.objects.filter(is_active=True),
        "faqs": FAQ.objects.filter(is_active=True, plan__isnull=True),
    })


def detail(request, slug):
    plan = get_object_or_404(WarrantyPlan, slug=slug, is_active=True)
    return render(request, "warranty/detail.html", {
        "plan": plan,
        "faqs": plan.faqs.filter(is_active=True),
        "other_plans": WarrantyPlan.objects.filter(is_active=True).exclude(pk=plan.pk),
    })
