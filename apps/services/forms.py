import datetime

from django import forms

from apps.catalog.models import Car
from apps.core.utils import to_latin_digits

from .booking import available_dates, date_label, slot_availability
from .models import Appointment, AppointmentSlot, Service


class AppointmentForm(forms.ModelForm):
    date = forms.ChoiceField(label="روز مراجعه")
    slot = forms.ModelChoiceField(
        label="ساعت مراجعه", queryset=AppointmentSlot.objects.filter(is_active=True), empty_label="انتخاب ساعت",
    )
    service = forms.ModelChoiceField(
        label="نوع خدمت", queryset=Service.objects.filter(is_active=True, bookable=True), empty_label="انتخاب خدمت",
    )
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1"}))

    class Meta:
        model = Appointment
        fields = ["full_name", "phone", "car_model", "plate_number", "mileage", "service", "date", "slot", "description"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "مثلاً علی محمدی"}),
            "phone": forms.TextInput(attrs={"placeholder": "۰۹۱۲۳۴۵۶۷۸۹", "dir": "ltr", "inputmode": "numeric"}),
            "car_model": forms.TextInput(attrs={"list": "car-models", "placeholder": "مثلاً شاهین"}),
            "plate_number": forms.TextInput(attrs={"placeholder": "اختیاری"}),
            "mileage": forms.NumberInput(attrs={"placeholder": "اختیاری", "dir": "ltr"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "شرح مختصر مشکل یا درخواست"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].choices = [("", "انتخاب روز")] + [(d.isoformat(), date_label(d)) for d in available_dates()]
        self.car_models = Car.objects.active().values_list("title", flat=True)

    def clean_phone(self):
        return to_latin_digits(self.cleaned_data["phone"]).replace(" ", "")

    def clean_date(self):
        try:
            return datetime.date.fromisoformat(self.cleaned_data["date"])
        except (TypeError, ValueError):
            raise forms.ValidationError("روز انتخاب‌شده معتبر نیست.")

    def clean(self):
        cleaned = super().clean()
        day, slot, phone = cleaned.get("date"), cleaned.get("slot"), cleaned.get("phone")
        if day and day not in available_dates():
            self.add_error("date", "این روز برای نوبت‌دهی در دسترس نیست.")
            return cleaned
        if day and slot:
            info = next((s for s in slot_availability(day) if s["id"] == slot.pk), None)
            if not info or not info["available"]:
                self.add_error("slot", "ظرفیت این ساعت تکمیل شده یا زمان آن گذشته است. لطفاً ساعت دیگری انتخاب کنید.")
        if day and phone and Appointment.objects.filter(date=day, phone=phone).exclude(
            status=Appointment.Status.CANCELLED
        ).exists():
            self.add_error("phone", "برای این شماره در این روز قبلاً نوبت ثبت شده است.")
        return cleaned


class TrackForm(forms.Form):
    code = forms.CharField(label="کد پیگیری", max_length=12, widget=forms.TextInput(attrs={"dir": "ltr", "inputmode": "numeric"}))
    phone = forms.CharField(label="شماره موبایل", max_length=11, widget=forms.TextInput(attrs={"dir": "ltr", "inputmode": "numeric"}))

    def clean_code(self):
        return to_latin_digits(self.cleaned_data["code"]).strip()

    def clean_phone(self):
        return to_latin_digits(self.cleaned_data["phone"]).strip()
