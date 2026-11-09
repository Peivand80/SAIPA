from django import template
from django.contrib.contenttypes.models import ContentType

from ..models import Like

register = template.Library()


@register.inclusion_tag("interactions/like_button.html", takes_context=True)
def like_button(context, obj):
    """دکمه لایک: {% load interactions %}{% like_button post %}"""
    request = context["request"]
    ct = ContentType.objects.get_for_model(obj)
    likes = Like.objects.filter(content_type=ct, object_id=obj.pk)
    session_key = request.session.session_key
    return {
        "target": f"{ct.app_label}.{ct.model}",
        "object_id": obj.pk,
        "count": likes.count(),
        "liked": bool(session_key) and likes.filter(session_key=session_key).exists(),
    }


@register.simple_tag
def like_count(obj):
    ct = ContentType.objects.get_for_model(obj)
    return Like.objects.filter(content_type=ct, object_id=obj.pk).count()
