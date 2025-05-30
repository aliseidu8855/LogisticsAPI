# apps/shipments/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import UserRole

class IsShipmentOwnerOrRelatedStaff(BasePermission):
    """
    Allows access if:
    - User is Admin or Warehouse Manager.
    - User is the Customer who owns the shipment.
    - User is a Dispatcher assigned to the delivery task of this shipment (for read mostly).
    """
    def has_object_permission(self, request, view, obj): 
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role == UserRole.ADMIN or user.role == UserRole.WAREHOUSE_MANAGER:
            return True

        if user.role == UserRole.CUSTOMER and obj.customer == user:
            return True

        if user.role == UserRole.DISPATCHER:
            if request.method in SAFE_METHODS: 
                try:
                    return obj.delivery_task is not None and obj.delivery_task.dispatcher == user
                except AttributeError: 
                    return False
            return False
        return False