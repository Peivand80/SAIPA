from django.urls import path

from . import views

app_name = "interactions"

urlpatterns = [
    path("like/", views.toggle_like, name="like"),
]
