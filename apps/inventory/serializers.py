# apps/inventory/serializers.py
from rest_framework import serializers
from django.db import transaction
from .models import Supplier, Warehouse, Product, ProductStock, ProductTransferLog
from apps.users.serializers import UserSimpleSerializer
from apps.containers.models import Container
# Removed: from apps.containers.serializers import ContainerSerializer # To break circular import

class SupplierSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class WarehouseSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class ProductSerializer(serializers.ModelSerializer):
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(), source='supplier', write_only=True, allow_null=True, required=False
    )
    container_id = serializers.PrimaryKeyRelatedField(
        queryset=Container.objects.all(), source='container', write_only=True, allow_null=True, required=False
    )

    supplier = SupplierSerializer(read_only=True)

    # Using SerializerMethodField for nested container details to break circular import
    container_details = serializers.SerializerMethodField(read_only=True)

    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'quantity', 'description',
            'supplier_id', 'supplier', 
            "expected_revenue",
            'total_cost_of_product',
            'expected_revenue', 
            'container_id',     
            'container_details', 
            'created_by', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'expected_revenue')

    def get_container_details(self, obj):
        if obj.container:
            # Local import to avoid circular dependency at module load time
            from apps.containers.serializers import ContainerSerializer
            return ContainerSerializer(obj.container, context=self.context).data
        return None

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class ProductStockSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    warehouse_id = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(), source='warehouse', write_only=True
    )
    product = ProductSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)

    class Meta:
        model = ProductStock
        fields = ('id', 'product_id', 'warehouse_id', 'product', 'warehouse', 'quantity', 'last_updated')
        read_only_fields = ('last_updated',)

class ProductTransferLogSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    from_warehouse = WarehouseSerializer(read_only=True)
    to_warehouse = WarehouseSerializer(read_only=True)
    transferred_by = UserSimpleSerializer(read_only=True)

    class Meta:
        model = ProductTransferLog
        fields = '__all__'

class ProductTransferActionSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), help_text="ID of the product to transfer.")
    from_warehouse_id = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all(), help_text="ID of the source warehouse.")
    to_warehouse_id = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all(), help_text="ID of the destination warehouse.")
    quantity = serializers.IntegerField(min_value=1, help_text="Quantity of the product to transfer.")
    notes = serializers.CharField(required=False, allow_blank=True, help_text="Optional notes for the transfer.")

    def validate_from_warehouse_id(self, value):
        if not value: # This check might be redundant if PrimaryKeyRelatedField handles it
            raise serializers.ValidationError("Source warehouse not found.")
        return value

    def validate_to_warehouse_id(self, value):
        if not value: # This check might be redundant
            raise serializers.ValidationError("Destination warehouse not found.")
        return value

    def validate(self, data):
        from_warehouse = data['from_warehouse_id']
        to_warehouse = data['to_warehouse_id']
        product = data['product_id']
        quantity_to_transfer = data['quantity']

        if from_warehouse == to_warehouse:
            raise serializers.ValidationError("Source and destination warehouses cannot be the same.")

        try:
            source_stock = ProductStock.objects.get(product=product, warehouse=from_warehouse)
            if source_stock.quantity < quantity_to_transfer:
                raise serializers.ValidationError(
                    f"Insufficient stock for product '{product.name}' in warehouse '{from_warehouse.name}'. "
                    f"Available: {source_stock.quantity}, Requested: {quantity_to_transfer}."
                )
        except ProductStock.DoesNotExist:
            raise serializers.ValidationError(
                f"Product '{product.name}' not found or no stock record in source warehouse '{from_warehouse.name}'."
            )
        return data

    def save(self):
        validated_data = self.validated_data
        product = validated_data['product_id']
        from_warehouse = validated_data['from_warehouse_id']
        to_warehouse = validated_data['to_warehouse_id']
        quantity = validated_data['quantity']
        notes = validated_data.get('notes', '')
        user = self.context['request'].user

        with transaction.atomic():
            # Ensure we lock the rows for update to prevent race conditions
            source_stock = ProductStock.objects.select_for_update().get(product=product, warehouse=from_warehouse)
            source_stock.quantity -= quantity
            source_stock.save()

            dest_stock, created = ProductStock.objects.select_for_update().get_or_create(
                product=product,
                warehouse=to_warehouse,
                defaults={'quantity': 0}
            )
            dest_stock.quantity += quantity
            dest_stock.save()

            log_entry = ProductTransferLog.objects.create(
                product=product,
                quantity=quantity,
                from_warehouse=from_warehouse,
                to_warehouse=to_warehouse,
                transferred_by=user,
                notes=notes
            )
            return log_entry