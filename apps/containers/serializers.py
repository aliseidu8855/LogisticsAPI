# apps/containers/serializers.py
from rest_framework import serializers
from .models import Container
from apps.users.serializers import UserSimpleSerializer
from apps.inventory.models import Warehouse
# Removed: from apps.inventory.serializers import WarehouseSerializer # To break circular import

class ContainerSerializer(serializers.ModelSerializer):
    created_by_details = UserSimpleSerializer(source="created_by", read_only=True)

    # Using SerializerMethodField for nested warehouse details to break circular import
    current_warehouse_details_data = serializers.SerializerMethodField(read_only=True)

    status_display = serializers.CharField(source="get_status_display", read_only=True)

    # This PrimaryKeyRelatedField is for writing the current_warehouse FK
    current_warehouse = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(),
        allow_null=True,
        required=False,
        write_only=True, # Important: this field is now only for input
        source='current_warehouse' # Explicitly link to model field for clarity
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
            "current_warehouse", # For write_only FK
            "current_warehouse_details_data", # For read_only nested object (from method)
            "current_goods_description",
            "last_known_origin",
            "created_by_details",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "container_id_code",
            # created_by_details is read_only by its definition
            "created_at",
            "updated_at",
            "status_display",
            # current_warehouse_details_data is read_only by its definition
        )

    def get_current_warehouse_details_data(self, obj):
        if obj.current_warehouse:
            # Local import to avoid circular dependency at module load time
            from apps.inventory.serializers import WarehouseSerializer
            return WarehouseSerializer(obj.current_warehouse, context=self.context).data
        return None