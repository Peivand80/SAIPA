from django.contrib import messages
from django.shortcuts import redirect

from apps.core.utils import get_client_ip, is_throttled, paginate

from .forms import CommentForm


class CommentableMixin:
    """
    این میکسین را به DetailView هر مدلی که فیلد GenericRelation به نام comments دارد اضافه کنید.
    نمایش نظرات تأییدشده، صفحه‌بندی آن‌ها و ثبت نظر جدید (در انتظار تأیید) را انجام می‌دهد.
    """

    def comments_enabled(self):
        return getattr(self.object, "allow_comments", True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        approved = self.object.comments.approved()
        context.update(
            {
                "comments_enabled": self.comments_enabled(),
                "comment_page": paginate(self.request, approved, "comments", page_param="cpage"),
                "comments_count": approved.count(),
                "comment_form": kwargs.get("comment_form") or CommentForm(),
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        target = self.object.get_absolute_url() + "#comments"
        if not self.comments_enabled():
            messages.error(request, "امکان ثبت نظر برای این مطلب بسته است.")
            return redirect(target)

        form = CommentForm(request.POST)
        if form.is_valid():
            if not form.is_spam():
                if is_throttled(request, "comment"):
                    messages.error(request, "تعداد نظرات ارسالی شما زیاد است. لطفاً چند دقیقه بعد دوباره تلاش کنید.")
                    return redirect(target)
                comment = form.save(commit=False)
                comment.content_object = self.object
                comment.ip_address = get_client_ip(request) or None
                comment.save()
            messages.success(request, "نظر شما ثبت شد و پس از تأیید مدیر سایت نمایش داده می‌شود. سپاسگزاریم.")
            return redirect(target)

        messages.error(request, "لطفاً خطاهای فرم نظر را برطرف کنید.")
        return self.render_to_response(self.get_context_data(comment_form=form))
