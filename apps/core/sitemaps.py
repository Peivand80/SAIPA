from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import Post
from apps.catalog.models import Car
from apps.core.models import Page
from apps.parts.models import Part
from apps.services.models import Service
from apps.warranty.models import WarrantyPlan


class StaticSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["core:home", "catalog:list", "services:list", "services:appointment", "parts:list",
                "warranty:index", "blog:list", "core:about", "contact:contact"]

    def location(self, item):
        return reverse(item)


class PostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Post.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class GenericSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def __init__(self, queryset):
        self.queryset = queryset
        super().__init__()

    def items(self):
        return self.queryset

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    "static": StaticSitemap,
    "posts": PostSitemap,
    "cars": GenericSitemap(Car.objects.filter(is_active=True)),
    "services": GenericSitemap(Service.objects.filter(is_active=True)),
    "parts": GenericSitemap(Part.objects.filter(is_active=True)),
    "warranty": GenericSitemap(WarrantyPlan.objects.filter(is_active=True)),
    "pages": GenericSitemap(Page.objects.filter(is_published=True)),
}
