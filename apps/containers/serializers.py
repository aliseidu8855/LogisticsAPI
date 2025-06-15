from rest_framework import serializers
from .models import Container
from apps.users.serializers import UserSimpleSerializer
from apps.inventory.serializers import WarehouseSerializer
from apps.inventory.models import Warehouse


class ContainerSerializer(serializers.ModelSerializer):
    created_by_details = UserSimpleSerializer(source="created_by", read_only=True)
    current_warehouse_details = WarehouseSerializer(
        source="current_warehouse", read_only=True
    )
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
            "current_warehouse",
            "current_warehouse_details",
            "current_goods_description",
            "last_known_origin",
            "created_by_details",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "container_id_code",
            "created_by_details",
            "created_at",
            "updated_at",
            "status_display",
            "current_warehouse_details",
        )
