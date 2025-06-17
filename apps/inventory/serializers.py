from rest_framework import serializers
from django.db import transaction
from .models import Supplier, Warehouse, Product, ProductStock, ProductTransferLog
from apps.users.serializers import UserSimpleSerializer
from apps.containers.models import Container


class SupplierSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Supplier
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "created_by")

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class WarehouseSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Warehouse
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "created_by")

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source="supplier",
        write_only=True,
        allow_null=True,
        required=False,
    )
    container_id = serializers.PrimaryKeyRelatedField(
        queryset=Container.objects.all(),
        source="container",
        write_only=True,
        allow_null=True,
        required=False,
    )

    supplier = SupplierSerializer(read_only=True)

    container_details = serializers.SerializerMethodField(read_only=True)

    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "quantity",
            "description",
            "supplier_id",
            "supplier",
            "cost_of_product",
            "selling_price",
            "total_cost_of_product",
            "expected_revenue",
            "container_id",
            "container_details",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "created_by",
            "expected_revenue",
        )

    def get_container_details(self, obj):
        if obj.container:
            from apps.containers.serializers import ContainerSerializer

            return ContainerSerializer(obj.container, context=self.context).data
        return None

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class ProductStockSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )
    warehouse_id = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(), source="warehouse", write_only=True
    )
    product = ProductSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)

    class Meta:
        model = ProductStock
        fields = (
            "id",
            "product_id",
            "warehouse_id",
            "product",
            "warehouse",
            "quantity",
            "last_updated",
        )
        read_only_fields = ("last_updated",)


class ProductTransferLogSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source="product", read_only=True)
    from_warehouse_details = WarehouseSerializer(
        source="from_warehouse", read_only=True
    )
    to_warehouse_details = WarehouseSerializer(source="to_warehouse", read_only=True)
    transferred_by_details = UserSimpleSerializer(
        source="transferred_by", read_only=True
    )

    class Meta:
        model = ProductTransferLog
        fields = (
            "id",
            "product",
            "product_details",
            "quantity_transferred",
            "from_warehouse",
            "from_warehouse_details",
            "to_warehouse",
            "to_warehouse_details",
            "transferred_by",
            "transferred_by_details",
            "timestamp",
            "description",
        )
        read_only_fields = fields


class ProductTransferActionSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), help_text="ID of the product to transfer."
    )
    to_warehouse = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(), help_text="ID of the destination warehouse."
    )
    quantity = serializers.IntegerField(
        min_value=1, help_text="Quantity of the product to transfer."
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        style={"base_template": "textarea.html"},
        help_text="Description or reason for the transfer.",
    )

    def validate_product(self, value):
        if not value:
            raise serializers.ValidationError("Product not found.")
        return value

    def validate_to_warehouse(self, value):
        if not value:
            raise serializers.ValidationError("Destination warehouse not found.")
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity to transfer must be greater than zero."
            )
        return value

    def validate(self, data):
        product_obj = data.get("product")
        # Get from_warehouse from product's container's current_warehouse
        from_warehouse_obj = None
        if product_obj and product_obj.container and product_obj.container.current_warehouse:
            from_warehouse_obj = product_obj.container.current_warehouse
        else:
            raise serializers.ValidationError({"product": "Product is not in a container with a warehouse."})
        to_warehouse_obj = data.get("to_warehouse")
        if from_warehouse_obj == to_warehouse_obj:
            raise serializers.ValidationError(
                {
                    "to_warehouse": "Source and destination warehouses cannot be the same."
                }
            )
        data["from_warehouse"] = from_warehouse_obj  # Pass to save()
        return data

    def save(self):
        validated_data = self.validated_data
        product_obj = validated_data["product"]
        from_warehouse_obj = validated_data["from_warehouse"]
        to_warehouse_obj = validated_data["to_warehouse"]
        quantity_transferred = validated_data["quantity"]
        description_text = validated_data.get("description", "")
        user = self.context["request"].user

        # Only log the transfer, do not check or update ProductStock
        log_entry = ProductTransferLog.objects.create(
            product=product_obj,
            quantity_transferred=quantity_transferred,
            from_warehouse=from_warehouse_obj,
            to_warehouse=to_warehouse_obj,
            transferred_by=user,
            description=description_text,
        )
        return log_entry
