"""آدرس‌های اصلی پروژه."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.sitemaps import sitemaps
from apps.core.views import robots_txt

admin.site.site_header = "پنل مدیریت نمایندگی سایپا - جدیدالاسلامی"
admin.site.site_title = "مدیریت سایت"
admin.site.index_title = "داشبورد"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt),
    path("", include("apps.core.urls")),
    path("cars/", include("apps.catalog.urls")),
    path("services/", include("apps.services.urls")),
    path("parts/", include("apps.parts.urls")),
    path("warranty/", include("apps.warranty.urls")),
    path("blog/", include("apps.blog.urls")),
    path("contact/", include("apps.contact.urls")),
    path("interactions/", include("apps.interactions.urls")),
    path("chatbot/", include("apps.chatbot.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "apps.core.views.error_404"
handler500 = "apps.core.views.error_500"
