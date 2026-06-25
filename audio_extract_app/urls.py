from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from audio_extract_app.accounts import signup
from audio_extract_app.pages import landing
from jobs.health import healthcheck

urlpatterns = [
    path("", landing, name="landing"),
    path("admin/", admin.site.urls),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("accounts/signup/", signup, name="signup"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("healthz/", healthcheck, name="healthcheck"),
    path("app/", include("jobs.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
