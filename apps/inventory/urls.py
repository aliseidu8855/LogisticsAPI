from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupplierViewSet, WarehouseViewSet, ProductViewSet,
    ProductStockViewSet, ProductTransferLogViewSet
)

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-stock', ProductStockViewSet)
router.register(r'product-transfer-logs', ProductTransferLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]