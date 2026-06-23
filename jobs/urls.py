from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.index, name="index"),
    path("jobs/<uuid:job_id>/", views.detail, name="detail"),
    path("jobs/<uuid:job_id>/status/", views.status, name="status"),
    path("jobs/<uuid:job_id>/download/<str:artifact>/", views.download, name="download"),
]
