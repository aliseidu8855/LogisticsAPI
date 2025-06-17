from rest_framework import serializers
from .models import ProductTransferLog
from apps.inventory.serializers import ProductSerializer, WarehouseSerializer

class ProductTransferLogSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    from_warehouse_details = WarehouseSerializer(source='from_warehouse', read_only=True)
    to_warehouse_details = WarehouseSerializer(source='to_warehouse', read_only=True)

    class Meta:
        model = ProductTransferLog
        fields = (
            'id',
            'product',
            'product_details',
            'from_warehouse',
            'from_warehouse_details',
            'to_warehouse',
            'to_warehouse_details',
            'quantity',
            'notes',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'product_details', 'from_warehouse_details', 'to_warehouse_details')
        

