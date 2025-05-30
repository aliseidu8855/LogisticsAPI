# apps/shipments/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Shipment, ShipmentItem
from .serializers import ShipmentSerializer, ShipmentItemSerializer
from apps.users.models import UserRole
from apps.users.permissions import IsAdminUserRole, IsWarehouseManagerRole
from .permissions import IsShipmentOwnerOrRelatedStaff


class ShipmentViewSet(viewsets.ModelViewSet):
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Shipment.objects.select_related(
            "customer", "container", "origin_warehouse", "created_by"
        ).prefetch_related("items__product", "delivery_task")

        if not user or not user.is_authenticated:
            return Shipment.objects.none()

        if user.role == UserRole.ADMIN or user.role == UserRole.WAREHOUSE_MANAGER:
            return queryset.all()
        elif user.role == UserRole.CUSTOMER:
            return queryset.filter(customer=user)
        elif user.role == UserRole.DISPATCHER:
            return queryset.filter(delivery_task__dispatcher=user)
        return Shipment.objects.none()

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ["create", "destroy"]:
            return [IsAuthenticated(), (IsAdminUserRole | IsWarehouseManagerRole)()]
        elif self.action in ["update", "partial_update", "retrieve"]:
            return [IsAuthenticated(), IsShipmentOwnerOrRelatedStaff()]
        return super().get_permissions()

    def perform_create(self, serializer):
        shipment = serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        shipment = serializer.save()
