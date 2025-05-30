from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ActionLog
from .serializers import ActionLogSerializer
from apps.users.permissions import IsAdminUserRole, IsWarehouseManagerRole 

class ActionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing action logs.
    Only accessible by Admins or Warehouse Managers.
    """
    queryset = ActionLog.objects.select_related('user', 'content_type').all()
    serializer_class = ActionLogSerializer
    permission_classes = [IsAuthenticated, (IsAdminUserRole | IsWarehouseManagerRole)]
    filterset_fields = ['user__email', 'action_verb', 'content_type__model', 'ip_address'] 
    search_fields = ['user__email', 'action_verb', 'details', 'object_id'] 
