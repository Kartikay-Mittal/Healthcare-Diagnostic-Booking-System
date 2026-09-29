from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication APIs
    path(
        "api/auth/",
        include("accounts.urls"),
    ),

    # Diagnostic centre APIs
    path(
        "api/",
        include("diagnostics.urls"),
    ),

    # Booking APIs
    path(
        "api/",
        include("bookings.urls"),
    ),

    # Payment APIs
    path(
        "api/",
        include("payments.urls"),
    ),

    # OpenAPI schema
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    # Swagger UI
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
        ),
        name="swagger-ui",
    ),
]