from rest_framework import viewsets, permissions
from .models import ProductTransferLog
from .serializers import ProductTransferLogSerializer
from apps.users.permissions import IsWarehouseManagerRole, IsAdminUserRole
class ProductTransferLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product transfer logs.
    """
    queryset = ProductTransferLog.objects.all()
    serializer_class = ProductTransferLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optionally filter by user or other criteria
        return self.queryset.filter(created_by=self.request.user)
    

