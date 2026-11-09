from django.urls import path

from . import views

app_name = "parts"

urlpatterns = [
    path("", views.PartListView.as_view(), name="list"),
    path("inquiry/", views.inquiry, name="inquiry"),
    path("<str:slug>/", views.part_detail, name="detail"),
]
