from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    Supplier,
    Warehouse,
    Product,
    ProductStock,
    ProductTransferLog,
)
from .serializers import (
    SupplierSerializer,
    WarehouseSerializer,
    ProductSerializer,
    ProductStockSerializer,
    ProductTransferLogSerializer,
    ProductTransferActionSerializer,
)
from apps.users.permissions import (
    IsWarehouseManagerRole,
    IsAdminUserRole,
)
from apps.audit_logs.services import (
    create_action_log,
)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        "supplier",
        "container",
        "created_by",
    ).all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["post"],
        url_path="transfer-stock",
        serializer_class=ProductTransferActionSerializer,
        permission_classes=[
            IsAuthenticated,
            IsWarehouseManagerRole | IsAdminUserRole,
        ],
    )
    def transfer_product_stock(self, request):
        """
        Transfers a specified quantity of a product from one warehouse to another.
        Updates stock levels and creates a transfer log.

        Required POST data:
        - product (ID)
        - from_warehouse (ID)
        - to_warehouse (ID)
        - quantity (integer)
        - description (string, optional)
        """
        serializer = ProductTransferActionSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            try:
                log_entry = serializer.save()

                create_action_log(
                    user=request.user,
                    action_verb="PRODUCT_STOCK_TRANSFERRED",
                    related_object=log_entry,
                    details={
                        "product_id": log_entry.product.id,
                        "product_sku": log_entry.product.sku,
                        "quantity": log_entry.quantity_transferred,
                        "from_warehouse": log_entry.from_warehouse.name,
                        "to_warehouse": log_entry.to_warehouse.name,
                        "description": log_entry.description,
                    },
                )

                return Response(
                    ProductTransferLogSerializer(log_entry).data,
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {
                        "error": "An error occurred during the transfer process.",
                        "details": str(e),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductStockViewSet(viewsets.ModelViewSet):
    queryset = ProductStock.objects.select_related(
        "product", "warehouse", "product__supplier"
    ).all()
    serializer_class = ProductStockSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = [
        "product",
        "warehouse",
    ]


class ProductTransferLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        ProductTransferLog.objects.select_related(
            "product", "from_warehouse", "to_warehouse", "transferred_by"
        )
        .all()
        .order_by("-timestamp")
    )
    serializer_class = ProductTransferLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["product", "from_warehouse", "to_warehouse", "transferred_by"]
    search_fields = [
        "product__name",
        "product__sku",
        "description",
        "transferred_by__email",
    ]
