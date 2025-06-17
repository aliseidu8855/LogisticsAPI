from rest_framework import serializers
from .models import Container
from apps.users.serializers import UserSimpleSerializer
from apps.inventory.models import Warehouse, Product
from apps.inventory.serializers import WarehouseSerializer, ProductSerializer


class ContainerSerializer(serializers.ModelSerializer):
    created_by_details = UserSimpleSerializer(source="created_by", read_only=True)
    current_warehouse_details_data = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    current_warehouse = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )

    class Meta:
        model = Container
        fields = (
            "id",
            "container_id_code",
            "type",
            "status",
            "status_display",
            "current_location_description",
            "bank_charges",
            "duty_and_ag_fess",
            "transportation_fees",
            "discharge",
            "calculate_purchased_cost",
            "calculate_expected_revenue",
            "expected_profit",
            "current_warehouse",
            "current_warehouse_details_data",
            "current_goods_description",
            "last_known_origin",
            "created_by_details",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "status_display",
            "calculate_purchased_cost",
            "calculate_expected_revenue",
            "expected_profit",
        )

    def get_current_warehouse_details_data(self, obj):
        if obj.current_warehouse:
            from apps.inventory.serializers import WarehouseSerializer

            return WarehouseSerializer(obj.current_warehouse, context=self.context).data
        return None


class ProductLinkedToContainer(serializers.ModelSerializer):
    container_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "quantity",
            "supplier",
            "container_details",
            "expected_revenue",
            "total_cost_of_product",
            "expected_profit",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def get_container_details(self, obj):
        if obj.container:
            return ContainerSerializer(obj.container, context=self.context).data
        return None
