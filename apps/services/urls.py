from django.urls import path

from . import views

app_name = "services"

urlpatterns = [
    path("", views.ServiceListView.as_view(), name="list"),
    path("appointment/", views.appointment, name="appointment"),
    path("appointment/done/", views.appointment_done, name="appointment_done"),
    path("appointment/availability/", views.availability, name="availability"),
    path("appointment/track/", views.track, name="track"),
    path("<str:slug>/", views.ServiceDetailView.as_view(), name="detail"),
]
