# apps/shipments/serializers.py
from rest_framework import serializers
from django.db import transaction
from .models import Shipment, ShipmentItem
from apps.users.serializers import UserSimpleSerializer
from apps.inventory.serializers import ProductSerializer, WarehouseSerializer
from apps.containers.serializers import ContainerSerializer
from apps.inventory.models import Product, Warehouse, ProductStock 
from apps.users.models import User, UserRole
from apps.containers.models import Container

class ShipmentItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ShipmentItem
        fields = ('id', 'product_id', 'product', 'quantity')

class ShipmentSerializer(serializers.ModelSerializer):
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=UserRole.CUSTOMER), source='customer', write_only=True
    )
    customer = UserSimpleSerializer(read_only=True)

    container_id = serializers.PrimaryKeyRelatedField(
        queryset=Container.objects.all(), source='container', write_only=True, allow_null=True, required=False
    )
    container = ContainerSerializer(read_only=True, allow_null=True)

    origin_warehouse_id = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(), source='origin_warehouse', write_only=True
    )
    origin_warehouse = WarehouseSerializer(read_only=True)

    items = ShipmentItemSerializer(many=True) # For creating/updating items with shipment
    created_by = UserSimpleSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Shipment
        fields = (
            'id', 'shipment_tracking_id',
            'customer_id', 'customer',
            'container_id', 'container',
            'origin_warehouse_id', 'origin_warehouse',
            'destination_address', 'status', 'status_display',
            'estimated_departure_date', 'actual_departure_date',
            'estimated_delivery_date', 'actual_delivery_date',
            'notes', 'customer_notes', 'items',
            'created_by', 'created_at', 'updated_at'
        )
        read_only_fields = ('shipment_tracking_id', 'created_at', 'updated_at', 'created_by', 'status_display')

    def validate_items(self, items_data):
        if not items_data:
            raise serializers.ValidationError("At least one shipment item is required.")
        product_ids = [item['product'].id for item in items_data] 
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("Duplicate products found in shipment items.")
        return items_data

    def validate(self, data):
        if self.instance is None: 
            origin_warehouse = data.get('origin_warehouse')
            items_data = data.get('items')
            if origin_warehouse and items_data:
                for item_data in items_data:
                    product = item_data['product']
                    quantity_requested = item_data['quantity']
                    try:
                        stock = ProductStock.objects.get(product=product, warehouse=origin_warehouse)
                        if stock.quantity < quantity_requested:
                            raise serializers.ValidationError(
                                f"Insufficient stock for product '{product.name}' in warehouse '{origin_warehouse.name}'. "
                                f"Available: {stock.quantity}, Requested: {quantity_requested}."
                            )
                    except ProductStock.DoesNotExist:
                        raise serializers.ValidationError(
                            f"Product '{product.name}' not found or no stock record in warehouse '{origin_warehouse.name}'."
                        )
        return data

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        validated_data['created_by'] = self.context['request'].user
        shipment = Shipment.objects.create(**validated_data)

        origin_warehouse = shipment.origin_warehouse
        for item_data in items_data:
            product = item_data['product'] # Product instance
            quantity_shipped = item_data['quantity']
            ShipmentItem.objects.create(shipment=shipment, product=product, quantity=quantity_shipped)
            try:
                stock_item = ProductStock.objects.select_for_update().get(
                    product=product,
                    warehouse=origin_warehouse
                )
                if stock_item.quantity < quantity_shipped:
                    raise serializers.ValidationError(f"Race condition or validation bypass: Insufficient stock for {product.name}.")
                stock_item.quantity -= quantity_shipped
                stock_item.save()
            except ProductStock.DoesNotExist:
                raise serializers.ValidationError(f"Race condition or validation bypass: Stock record not found for {product.name} in {origin_warehouse.name}.")
        return shipment

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        shipment = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                ShipmentItem.objects.create(shipment=instance, **item_data)
        return shipment