from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db import transaction, models
from rest_framework.authentication import SessionAuthentication, TokenAuthentication


from .models import Container
from .serializers import ContainerSerializer
from apps.users.permissions import IsAdminUserRole, IsWarehouseManagerRole
from apps.audit_logs.services import create_action_log
from apps.inventory.models import Warehouse


class ContainerViewSet(viewsets.ModelViewSet):
    queryset = Container.objects.select_related("current_warehouse", "created_by").all()
    serializer_class = ContainerSerializer  # Use the main serializer for all actions
    permission_classes = [IsAuthenticated]

    # permission_classes = [IsAuthenticated, IsAdminUserRole | IsWarehouseManagerRole]
    # permission_classes = [permissions.AllowAny]
    # authentication_classes = [TokenAuthentication, SessionAuthentication]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "status": ["exact", "in"],
        "type": ["exact", "icontains"],
        "current_warehouse": ["exact"],
        "current_warehouse__name": ["icontains"],
        "created_at": ["date", "year", "month", "day", "gte", "lte"],
        "updated_at": ["date", "year", "month", "day", "gte", "lte"],
    }
    search_fields = [
        "container_id_code",
        "current_location_description",
        "type",
        "current_goods_description",
        "last_known_origin",
    ]
    ordering_fields = [
        "container_id_code",
        "type",
        "status",
        "updated_at",
        "created_at",
        "current_warehouse__name",
    ]
    ordering = ["-updated_at"]

    def perform_create(self, serializer):
        container = serializer.save(created_by=self.request.user)
        create_action_log(
            user=self.request.user,
            action_verb="CONTAINER_CREATED",
            related_object=container,
            details={
                "id_code": container.container_id_code,
                "type": container.type,
                "status": container.status,
            },
        )

    def perform_update(self, serializer):
        instance_before_update = Container.objects.select_related(
            "current_warehouse"
        ).get(pk=self.get_object().pk)

        updated_fields_data = serializer.validated_data
        changed_fields_log = {}

        for field_name, new_value in updated_fields_data.items():
            old_value = getattr(instance_before_update, field_name)
            if isinstance(old_value, models.Model) and isinstance(
                new_value, models.Model
            ):
                if old_value.pk != new_value.pk:
                    changed_fields_log[field_name] = {
                        "old": old_value.pk if old_value else None,
                        "new": new_value.pk if new_value else None,
                        "old_display": str(old_value) if old_value else "None",
                        "new_display": str(new_value) if new_value else "None",
                    }
            elif isinstance(old_value, models.Model) and new_value is None:
                if old_value is not None:
                    changed_fields_log[field_name] = {
                        "old": old_value.pk,
                        "new": None,
                        "old_display": str(old_value),
                        "new_display": "None",
                    }
            elif old_value is None and isinstance(new_value, models.Model):
                if new_value is not None:
                    changed_fields_log[field_name] = {
                        "old": None,
                        "new": new_value.pk,
                        "old_display": "None",
                        "new_display": str(new_value),
                    }
            elif old_value != new_value:
                changed_fields_log[field_name] = {
                    "old": str(old_value),
                    "new": str(new_value),
                }

        container = serializer.save()

        if changed_fields_log:
            create_action_log(
                user=self.request.user,
                action_verb="CONTAINER_UPDATED",
                related_object=container,
                details={
                    "id_code": container.container_id_code,
                    "changes": changed_fields_log,
                },
            )

    def perform_destroy(self, instance):
        create_action_log(
            user=self.request.user,
            action_verb="CONTAINER_DELETED",
            details={
                "id_code": instance.container_id_code,
                "type": instance.type,
                "id": instance.id,
            },
        )
        instance.delete()

    @action(detail=True, methods=["post"], url_path="transfer-warehouse")
    @transaction.atomic
    def transfer_warehouse(self, request, pk=None):
        container = self.get_object()
        new_warehouse_id = request.data.get("new_warehouse_id")

        if not new_warehouse_id:
            return Response(
                {"error": "new_warehouse_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_warehouse = Warehouse.objects.get(pk=new_warehouse_id)
        except Warehouse.DoesNotExist:
            return Response(
                {"error": "Target warehouse not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if container.current_warehouse == new_warehouse:
            return Response(
                {"message": "Container is already at this warehouse."},
                status=status.HTTP_200_OK,
            )

        old_warehouse = container.current_warehouse
        container.current_warehouse = new_warehouse
        container.current_location_description = f"At {new_warehouse.name}"
        container.save()

        create_action_log(
            user=request.user,
            action_verb="CONTAINER_TRANSFERRED_WAREHOUSE",
            related_object=container,
            details={
                "id_code": container.container_id_code,
                "from_warehouse_id": old_warehouse.id if old_warehouse else None,
                "from_warehouse_name": (
                    old_warehouse.name if old_warehouse else "No previous warehouse"
                ),
                "to_warehouse_id": new_warehouse.id,
                "to_warehouse_name": new_warehouse.name,
            },
        )
        serializer = self.get_serializer(container)
        return Response(serializer.data, status=status.HTTP_200_OK)
