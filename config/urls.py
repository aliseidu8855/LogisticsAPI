from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt

schema_view = get_schema_view(
    openapi.Info(
        title="Logistics API",
        default_version="v1",
        description="API documentation for Logistics",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="aliseidu8855@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny]
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/users/", include("apps.users.urls")),
    path("api/inventory/", include("apps.inventory.urls")),
    path("api/containers/", include("apps.containers.urls")),
    path("api/shipments/", include("apps.shipments.urls")),
    path("api/deliveries/", include("apps.deliveries.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/audit/", include("apps.audit_logs.urls")),
    # path("api/transfer/", include("apps.transfer.urls")),
    # Swagger UI:
    re_path(
        r"^swagger/$",
        csrf_exempt(schema_view.with_ui("swagger", cache_timeout=0)),
        name="schema-swagger-ui",
    ),
    # ReDoc UI:
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    # Raw schema (JSON or YAML):
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
]
