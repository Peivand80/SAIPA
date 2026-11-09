from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static
from django.urls import reverse

from apps.blog.models import Post
from apps.catalog.models import Car
from apps.parts.models import Part
from apps.services.models import Service
from apps.warranty.models import WarrantyPlan

from apps.chatbot.engine import greeting_text, quick_replies

from .defaults import ABOUT_IMAGE, car_strip, showcase_photos, videos
from .models import HomeStat, Page, ShowcasePhoto, TeamMember, Video
from .utils import paginate


def home(request):
    featured_cars = Car.objects.active().filter(is_featured=True).select_related("category")[:6]
    if not featured_cars:
        featured_cars = Car.objects.active().select_related("category")[:6]
    photos = showcase_photos(ShowcasePhoto.objects.filter(is_active=True))
    # سه ستون تصویر متحرک با ترتیب متفاوت
    photo_columns = [photos[i:] + photos[:i] for i in (0, 2, 1)] if photos else []
    context = {
        "cars": featured_cars,
        "photo_columns": photo_columns,
        "car_strip": car_strip(Car.objects.active().select_related("category")[:12]),
        "photos": photos,
        "services": Service.objects.active()[:6],
        "posts": Post.objects.published().select_related("category")[:3],
        "plans": WarrantyPlan.objects.filter(is_active=True)[:3],
        "stats": HomeStat.objects.all()[:4],
        "about_image": static(ABOUT_IMAGE),
        "bot_quick": quick_replies(),
        "bot_greeting": greeting_text(),
    }
    context["reels"], context["band_video"] = videos(Video.objects.filter(is_active=True))
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html", {
        "team": TeamMember.objects.filter(is_active=True),
        "photos": showcase_photos(ShowcasePhoto.objects.filter(is_active=True)),
        "about_image": static(ABOUT_IMAGE),
        "band_video": videos(Video.objects.filter(is_active=True))[1],
    })


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_published=True)
    return render(request, "core/page_detail.html", {"page": page})


def search(request):
    q = request.GET.get("q", "").strip()
    results = []
    if len(q) >= 2:
        for post in Post.objects.published().filter(
            Q(title__icontains=q) | Q(summary__icontains=q) | Q(body__icontains=q)
        )[:50]:
            results.append({"kind": "مطلب", "title": post.title, "summary": post.summary,
                            "url": post.get_absolute_url(), "image": post.cover})
        for car in Car.objects.active().filter(Q(title__icontains=q) | Q(summary__icontains=q))[:20]:
            results.append({"kind": "خودرو", "title": car.title, "summary": car.summary,
                            "url": car.get_absolute_url(), "image": car.image})
        for service in Service.objects.active().filter(Q(title__icontains=q) | Q(summary__icontains=q))[:20]:
            results.append({"kind": "خدمت", "title": service.title, "summary": service.summary,
                            "url": service.get_absolute_url(), "image": service.image})
        for part in Part.objects.filter(is_active=True).filter(Q(title__icontains=q) | Q(code__icontains=q))[:50]:
            results.append({"kind": "قطعه", "title": str(part), "summary": part.description[:160],
                            "url": part.get_absolute_url(), "image": part.image})
        for plan in WarrantyPlan.objects.filter(is_active=True).filter(
            Q(title__icontains=q) | Q(summary__icontains=q)
        ):
            results.append({"kind": "گارانتی", "title": plan.title, "summary": plan.summary,
                            "url": plan.get_absolute_url(), "image": plan.image})
    page_obj = paginate(request, results, "search")
    return render(request, "core/search.html", {"q": q, "page_obj": page_obj, "total": len(results)})


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /ckeditor5/",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def error_404(request, exception):
    return render(request, "404.html", status=404)


def error_500(request):
    return render(request, "500.html", status=500)
