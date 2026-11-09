from django.conf import settings
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from apps.interactions.mixins import CommentableMixin

from .models import Category, Post


class PostListView(ListView):
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = settings.PAGINATION["posts"]

    def get_queryset(self):
        qs = Post.objects.published().select_related("category")
        self.category = None
        if "slug" in self.kwargs:
            self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
            qs = qs.filter(category=self.category)
        self.q = self.request.GET.get("q", "").strip()
        if self.q:
            qs = qs.filter(Q(title__icontains=self.q) | Q(summary__icontains=self.q) | Q(body__icontains=self.q))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"categories": Category.objects.all(), "category": self.category, "q": self.q})
        return context


class PostDetailView(CommentableMixin, DetailView):
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        qs = Post.objects.select_related("category", "author")
        # مدیر سایت پیش‌نویس‌ها را هم می‌بیند (برای پیش‌نمایش)
        return qs if self.request.user.is_staff else qs.published()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        viewed = request.session.get("viewed_posts", [])
        if self.object.pk not in viewed:
            Post.objects.filter(pk=self.object.pk).update(views=F("views") + 1)
            request.session["viewed_posts"] = (viewed + [self.object.pk])[-200:]
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related = Post.objects.published().exclude(pk=self.object.pk)
        if self.object.category_id:
            related = related.filter(category_id=self.object.category_id)
        context["related"] = related[:3]
        context["share_url"] = self.request.build_absolute_uri(self.object.get_absolute_url())
        return context
