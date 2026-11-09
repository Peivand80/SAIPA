from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from .models import Like


def get_target(label, object_id):
    """فقط مدل‌های مجاز (INTERACTION_MODELS) قابل لایک هستند."""
    if label not in settings.INTERACTION_MODELS:
        raise Http404
    model = apps.get_model(label)
    return get_object_or_404(model, pk=object_id)


@require_POST
def toggle_like(request):
    obj = get_target(request.POST.get("target", ""), request.POST.get("id"))
    if not request.session.session_key:
        request.session["visitor"] = True
        request.session.save()
    ct = ContentType.objects.get_for_model(obj)
    like, created = Like.objects.get_or_create(
        content_type=ct, object_id=obj.pk, session_key=request.session.session_key
    )
    if not created:
        like.delete()
    count = Like.objects.filter(content_type=ct, object_id=obj.pk).count()
    return JsonResponse({"liked": created, "count": count})
