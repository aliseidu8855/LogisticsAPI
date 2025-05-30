from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import UserRole

class IsDeliveryTaskAssigneeOrManager(BasePermission):
    """
    Allows access if:
    - User is Admin or Warehouse Manager (can manage all tasks).
    - User is the Dispatcher assigned to this specific delivery task.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or view.action == 'create':
            return request.user and request.user.is_authenticated and \
                   (request.user.role == UserRole.ADMIN or request.user.role == UserRole.WAREHOUSE_MANAGER)
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj): 
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role == UserRole.ADMIN or user.role == UserRole.WAREHOUSE_MANAGER:
            return True

        if user.role == UserRole.DISPATCHER and obj.dispatcher == user:
            return True

        return False

class CanCreateDeliveryTask(BasePermission):
    """
    Only Warehouse Managers or Admins can create delivery tasks.
    """
    def has_permission(self, request, view):
        if request.method == 'POST': 
            return request.user and request.user.is_authenticated and \
                   (request.user.role == UserRole.ADMIN or request.user.role == UserRole.WAREHOUSE_MANAGER)
        return True