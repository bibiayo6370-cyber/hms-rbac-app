"""
Root URL configuration.

/admin/            Django admin (data inspection/administration)
/api/auth/          Login, token refresh, current-user profile
/api/dashboard/      Administrative dashboard metrics (Module 6)

Module routers (patients, clinical, laboratory, pharmacy, billing) are
intended to be added here as `path("api/patients/", include("patients.urls"))`
etc. in the same pattern as accounts/dashboard, sprint by sprint
(Section 3.1.4). Scaffolds for those apps already exist and follow the
identical models -> serializers -> views -> urls structure used below.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/dashboard/", include("dashboard.urls")),
]
