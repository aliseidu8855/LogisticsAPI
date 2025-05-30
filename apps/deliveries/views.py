# apps/deliveries/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import DeliveryTask
from .serializers import DeliveryTaskSerializer, DeliveryTaskUpdateByDispatcherSerializer
from apps.users.models import UserRole
from apps.users.permissions import IsAdminUserRole, IsWarehouseManagerRole
from .permissions import IsDeliveryTaskAssigneeOrManager, CanCreateDeliveryTask


class DeliveryTaskViewSet(viewsets.ModelViewSet):
    queryset = DeliveryTask.objects.select_related(
        'shipment__customer', 'shipment__origin_warehouse', 'dispatcher'
    ).all()
    serializer_class = DeliveryTaskSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), CanCreateDeliveryTask()]
        return [IsAuthenticated(), IsDeliveryTaskAssigneeOrManager()]

    def get_serializer_class(self):
        user = self.request.user

        if user and user.is_authenticated and user.role == UserRole.DISPATCHER and \
           self.action in ['update', 'partial_update']:
            return DeliveryTaskUpdateByDispatcherSerializer
        return DeliveryTaskSerializer 

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if not user or not user.is_authenticated:
            return DeliveryTask.objects.none()

        if user.role == UserRole.ADMIN or user.role == UserRole.WAREHOUSE_MANAGER:
            shipment_id = self.request.query_params.get('shipment_id')
            status_param = self.request.query_params.get('status')
            dispatcher_id_param = self.request.query_params.get('dispatcher_id')

            if shipment_id:
                queryset = queryset.filter(shipment_id=shipment_id)
            if status_param:
                queryset = queryset.filter(status=status_param)
            if dispatcher_id_param:
                queryset = queryset.filter(dispatcher_id=dispatcher_id_param)
            return queryset
        elif user.role == UserRole.DISPATCHER:
            return queryset.filter(dispatcher=user)
        return DeliveryTask.objects.none() 

    @action(detail=False, methods=['get'], url_path='assigned-to-me', permission_classes=[IsAuthenticated])
    def assigned_to_me(self, request):
        """
        Convenience endpoint for dispatchers to get their currently assigned tasks.
        """
        user = request.user
        if user.role != UserRole.DISPATCHER:
            return Response(
                {"detail": "This endpoint is for dispatchers only."},
                status=status.HTTP_403_FORBIDDEN
            )
        tasks = DeliveryTask.objects.filter(
            dispatcher=user
        ).exclude(
            status__in=[DeliveryTask.DeliveryStatus.DELIVERED, DeliveryTask.DeliveryStatus.RETURNED, DeliveryTask.DeliveryStatus.CANCELLED]
        ).order_by('scheduled_pickup_datetime', 'scheduled_delivery_datetime')
       

        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='mark-picked-up')
    def mark_picked_up(self, request, pk=None):
        task = self.get_object() 
        if task.status not in [DeliveryTask.DeliveryStatus.ASSIGNED, DeliveryTask.DeliveryStatus.AWAITING_PICKUP]:
            return Response({"error": f"Cannot mark as picked up from status {task.get_status_display()}"}, status=status.HTTP_400_BAD_REQUEST)
        task.status = DeliveryTask.DeliveryStatus.PICKED_UP
        task.actual_pickup_datetime = timezone.now()
        task.save()
        return Response(DeliveryTaskSerializer(task).data)

    @action(detail=True, methods=['post'], url_path='mark-delivered')
    def mark_delivered(self, request, pk=None):
        task = self.get_object()
        if task.status not in [DeliveryTask.DeliveryStatus.IN_TRANSIT_LOCAL, DeliveryTask.DeliveryStatus.ARRIVED_CUSTOMER]:
             return Response({"error": f"Cannot mark as delivered from status {task.get_status_display()}"}, status=status.HTTP_400_BAD_REQUEST)
        task.recipient_name = request.data.get('recipient_name', task.recipient_name)
        task.signature_data = request.data.get('signature_data', task.signature_data)


        task.status = DeliveryTask.DeliveryStatus.DELIVERED
        task.actual_delivery_datetime = timezone.now()
        task.save()
        return Response(DeliveryTaskSerializer(task).data)