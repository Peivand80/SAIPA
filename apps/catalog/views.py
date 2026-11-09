from django.conf import settings
from django.db.models import Q
from django.views.generic import DetailView, ListView

from apps.interactions.mixins import CommentableMixin

from .models import Car, CarCategory


class CarListView(ListView):
    template_name = "catalog/car_list.html"
    context_object_name = "cars"
    paginate_by = settings.PAGINATION["cars"]

    def get_queryset(self):
        qs = Car.objects.active().select_related("category")
        self.category = self.request.GET.get("category", "")
        self.q = self.request.GET.get("q", "").strip()
        if self.category:
            qs = qs.filter(category__slug=self.category)
        if self.q:
            qs = qs.filter(Q(title__icontains=self.q) | Q(summary__icontains=self.q))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"categories": CarCategory.objects.all(), "current_category": self.category, "q": self.q})
        return context


class CarDetailView(CommentableMixin, DetailView):
    template_name = "catalog/car_detail.html"
    context_object_name = "car"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Car.objects.active().select_related("category").prefetch_related("specs", "images", "colors")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = {}
        for spec in self.object.specs.all():
            groups.setdefault(spec.group or "مشخصات", []).append(spec)
        context["spec_groups"] = groups
        context["related"] = Car.objects.active().exclude(pk=self.object.pk)[:3]
        context["compatible_parts"] = self.object.parts.filter(is_active=True)[:8]
        return context
