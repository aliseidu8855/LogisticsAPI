# apps/containers/serializers.py
from rest_framework import serializers
from .models import Container
from apps.users.serializers import UserSimpleSerializer
from apps.inventory.serializers import WarehouseSerializer 
from apps.users.models import User, UserRole 
from apps.inventory.models import Warehouse  

class ContainerSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    assigned_customer_details = UserSimpleSerializer(source='assigned_customer', read_only=True)
    current_warehouse_details = WarehouseSerializer(source='current_warehouse', read_only=True)

    assigned_customer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=UserRole.CUSTOMER),
        allow_null=True, required=False, write_only=True
    )
    current_warehouse = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(), 
        allow_null=True, required=False, write_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)


    class Meta:
        model = Container
        fields = (
            'id', 'container_id_code', 'type', 'status', 'status_display',
            'current_location_description',
            'current_warehouse', 'current_warehouse_details', 
            'assigned_customer', 'assigned_customer_details',
            'created_by', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'status_display')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        container = super().update(instance, validated_data)
        return container