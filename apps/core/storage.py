"""محل ذخیره تصاویری که داخل متن مطالب (ویرایشگر CKEditor) آپلود می‌شوند: media/editor/YYYY/MM/"""
import datetime
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class EditorStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("location", os.path.join(settings.MEDIA_ROOT, "editor"))
        kwargs.setdefault("base_url", settings.MEDIA_URL + "editor/")
        super().__init__(*args, **kwargs)

    def get_available_name(self, name, max_length=None):
        name = os.path.join(datetime.date.today().strftime("%Y/%m"), os.path.basename(name))
        return super().get_available_name(name, max_length)
