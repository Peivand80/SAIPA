from django import forms

from apps.core.utils import to_latin_digits

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1"}))

    class Meta:
        model = ContactMessage
        fields = ["full_name", "phone", "email", "subject", "message"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "نام و نام خانوادگی"}),
            "phone": forms.TextInput(attrs={"placeholder": "شماره تماس", "dir": "ltr", "inputmode": "numeric"}),
            "email": forms.EmailInput(attrs={"placeholder": "اختیاری", "dir": "ltr"}),
            "message": forms.Textarea(attrs={"rows": 5, "placeholder": "پیام خود را بنویسید..."}),
        }

    def clean_phone(self):
        phone = to_latin_digits(self.cleaned_data["phone"]).replace(" ", "").replace("-", "")
        if not phone.isdigit() or not 8 <= len(phone) <= 13:
            raise forms.ValidationError("شماره تماس معتبر نیست.")
        return phone
