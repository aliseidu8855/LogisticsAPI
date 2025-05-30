from rest_framework import serializers
from .models import DeliveryTask
from apps.shipments.serializers import ShipmentSerializer
from apps.users.serializers import UserSimpleSerializer
from apps.shipments.models import Shipment
from apps.users.models import User, UserRole


class DeliveryTaskSerializer(serializers.ModelSerializer):
    shipment_id = serializers.PrimaryKeyRelatedField(
        queryset=Shipment.objects.all(), source="shipment", write_only=True
    )
    shipment = ShipmentSerializer(read_only=True)

    dispatcher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=UserRole.DISPATCHER),
        source="dispatcher",
        write_only=True,
        allow_null=True,
        required=False,
    )
    dispatcher = UserSimpleSerializer(read_only=True, allow_null=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    pickup_address = serializers.CharField(source="get_pickup_address", read_only=True)
    delivery_address = serializers.CharField(
        source="get_delivery_address", read_only=True
    )

    class Meta:
        model = DeliveryTask
        fields = (
            "id",
            "shipment_id",
            "shipment",
            "dispatcher_id",
            "dispatcher",
            "status",
            "status_display",
            "pickup_address_override",
            "scheduled_pickup_datetime",
            "actual_pickup_datetime",
            "pickup_address",
            "delivery_address_override",
            "scheduled_delivery_datetime",
            "actual_delivery_datetime",
            "delivery_address",
            "recipient_name",
            "signature_data",
            "dispatcher_notes",
            "internal_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "status_display",
            "pickup_address",
            "delivery_address",
        )

    def validate_shipment_id(self, value):
        if (
            DeliveryTask.objects.filter(shipment=value).exists()
            and self.instance is None
        ):  # On create
            raise serializers.ValidationError(
                "A delivery task already exists for this shipment."
            )
        if self.instance and self.instance.shipment != value:
            if DeliveryTask.objects.filter(shipment=value).exists():
                raise serializers.ValidationError(
                    "A delivery task already exists for the new shipment."
                )
        return value

    def create(self, validated_data):
        task = DeliveryTask.objects.create(**validated_data)
        return task

    def update(self, instance, validated_data):

        task = super().update(instance, validated_data)
        return task


class DeliveryTaskUpdateByDispatcherSerializer(serializers.ModelSerializer):
    """
    A more restricted serializer for dispatchers to update their tasks.
    They can mainly update status, actual datetimes, notes, and PoD.
    """

    class Meta:
        model = DeliveryTask
        fields = (
            "status",
            "actual_pickup_datetime",
            "actual_delivery_datetime",
            "recipient_name",
            "signature_data",
            "dispatcher_notes",
        )
