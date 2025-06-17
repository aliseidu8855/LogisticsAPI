from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Supplier, Warehouse, Product, ProductStock, ProductTransferLog
from .serializers import (
    SupplierSerializer,
    WarehouseSerializer,
    ProductSerializer,
    ProductStockSerializer,
    ProductTransferLogSerializer,
    ProductTransferActionSerializer,
)
from apps.users.permissions import IsWarehouseManagerRole, IsAdminUserRole


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    # permission_classes = [IsAuthenticated, IsAdminUserRole | IsWarehouseManagerRole]
    permission_classes = [IsAuthenticated]



class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    # permission_classes = [IsAuthenticated, IsAdminUserRole | IsWarehouseManagerRole]
    permission_classes = [IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        "supplier", "container", "created_by"
    ).all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsAuthenticated, IsAdminUserRole | IsWarehouseManagerRole]


    @action(
        detail=False,
        methods=["post"],
        url_path="transfer-stock",
        serializer_class=ProductTransferActionSerializer,
    )
    def transfer_stock(self, request):
        """
        Transfers product stock between two warehouses.
        Expects: product_id, from_warehouse_id, to_warehouse_id, quantity, notes (optional)
        """
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            log_entry = serializer.save()
            return Response(
                ProductTransferLogSerializer(log_entry).data, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductStockViewSet(viewsets.ModelViewSet):
    queryset = ProductStock.objects.select_related(
        "product", "warehouse", "product__supplier"
    ).all()
    serializer_class = ProductStockSerializer
    # permission_classes = [IsAuthenticated, IsAdminUserRole | IsWarehouseManagerRole]
    permission_classes = [IsAuthenticated]


class ProductTransferLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductTransferLog.objects.select_related(
        "product", "from_warehouse", "to_warehouse", "transferred_by"
    ).all()
    serializer_class = ProductTransferLogSerializer
    # permission_classes = [IsAuthenticated, IsAdminUserRole | IsWarehouseManagerRole]
    permission_classes = [IsAuthenticated]
