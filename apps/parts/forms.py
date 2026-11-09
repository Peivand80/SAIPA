from django import forms

from apps.core.utils import to_latin_digits

from .models import PartInquiry


class PartInquiryForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1"}))

    class Meta:
        model = PartInquiry
        fields = ["part_name", "car_model", "full_name", "phone", "message"]
        widgets = {
            "part_name": forms.TextInput(attrs={"placeholder": "نام یا کد قطعه"}),
            "car_model": forms.TextInput(attrs={"list": "car-models", "placeholder": "مثلاً ساینا"}),
            "full_name": forms.TextInput(attrs={"placeholder": "نام شما"}),
            "phone": forms.TextInput(attrs={"placeholder": "۰۹۱۲۳۴۵۶۷۸۹", "dir": "ltr", "inputmode": "numeric"}),
            "message": forms.Textarea(attrs={"rows": 3, "placeholder": "توضیحات (اختیاری)"}),
        }

    def clean_phone(self):
        return to_latin_digits(self.cleaned_data["phone"]).replace(" ", "")
