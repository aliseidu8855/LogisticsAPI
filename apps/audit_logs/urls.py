from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActionLogViewSet

router = DefaultRouter()
router.register(r'action-logs', ActionLogViewSet, basename='actionlog') # /api/audit/action-logs/

urlpatterns = [
    path('', include(router.urls)),
]