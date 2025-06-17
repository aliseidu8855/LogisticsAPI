from django.urls import path, include
from .views import ProductTransferLogViewSet

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'product-transfer-logs', ProductTransferLogViewSet, basename='product-transfer-logs')
urlpatterns = [
    path('', include(router.urls)),
]