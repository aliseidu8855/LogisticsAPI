# apps/containers/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Container
from .serializers import ContainerSerializer
from apps.users.permissions import IsAdminUserRole, IsWarehouseManagerRole

class ContainerViewSet(viewsets.ModelViewSet):
    queryset = Container.objects.select_related(
        'current_warehouse', 'assigned_customer', 'created_by'
    ).all()
    serializer_class = ContainerSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole | IsWarehouseManagerRole]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        assigned_customer_param = self.request.query_params.get('assigned_customer_id')

        if status_param:
            queryset = queryset.filter(status=status_param)
        if assigned_customer_param:
            queryset = queryset.filter(assigned_customer_id=assigned_customer_param)

        return queryset