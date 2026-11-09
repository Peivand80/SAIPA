from django.urls import path

from . import views

app_name = "warranty"

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:slug>/", views.detail, name="detail"),
]
