from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    # فیلد تله برای ربات‌ها؛ برای کاربر واقعی مخفی است و باید خالی بماند
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1"}))

    class Meta:
        model = Comment
        fields = ["name", "email", "body"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "نام شما"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@example.com", "dir": "ltr"}),
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "نظر یا پرسش خود را بنویسید..."}),
        }
        labels = {"email": "ایمیل (اختیاری)"}

    def clean_body(self):
        body = self.cleaned_data["body"].strip()
        if len(body) < 5:
            raise forms.ValidationError("متن نظر خیلی کوتاه است.")
        if body.count("http") > 2:
            raise forms.ValidationError("ارسال لینک‌های متعدد مجاز نیست.")
        return body

    def is_spam(self):
        return bool(self.cleaned_data.get("website"))
