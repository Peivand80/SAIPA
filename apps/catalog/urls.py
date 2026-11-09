from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.CarListView.as_view(), name="list"),
    path("<str:slug>/", views.CarDetailView.as_view(), name="detail"),
]
