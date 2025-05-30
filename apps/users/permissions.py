# apps/users/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import UserRole

class IsAdminUserRole(BasePermission):
    """
    Allows access only to users with the ADMIN role or superusers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == UserRole.ADMIN or request.user.is_superuser)
        )

class IsWarehouseManagerRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.WAREHOUSE_MANAGER
        )

class IsCustomerRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.CUSTOMER
        )

class IsDispatcherRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.DISPATCHER
        )

class IsOwnerOrAdminOrSuperuser(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it,
    or if the user is an Admin (role) or Superuser.
    Assumes the object instance has an `id` that matches `request.user.id` for ownership.
    For objects with a `user` or `customer` foreign key, adjust accordingly.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            obj == request.user or
            (request.user and request.user.is_authenticated and \
             (request.user.role == UserRole.ADMIN or request.user.is_superuser))
        )

class CanManageUser(BasePermission):
    """
    Permission to check if a user can manage (list, retrieve, create, update, delete) other users.
    - Admins/Superusers can manage any user.
    - Warehouse Managers might be able to create Customers/Dispatchers but not other WMs or Admins.
    - Users can view/update their own profile.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method == 'POST':
            return request.user.role == UserRole.ADMIN or \
                   request.user.is_superuser or \
                   request.user.role == UserRole.WAREHOUSE_MANAGER 

        if request.method == 'GET' and view.action == 'list':
            return request.user.role == UserRole.ADMIN or \
                   request.user.is_superuser or \
                   request.user.role == UserRole.WAREHOUSE_MANAGER

        return True 

    def has_object_permission(self, request, view, obj_user): 
        if not request.user or not request.user.is_authenticated:
            return False

        if view.action == 'retrieve' and obj_user == request.user:
            return True

        if request.user.role == UserRole.ADMIN or request.user.is_superuser:
            return True

        if view.action in ['update', 'partial_update', 'change_password_action'] and obj_user == request.user:
            return True

        if request.user.role == UserRole.WAREHOUSE_MANAGER:
            if obj_user.role in [UserRole.CUSTOMER, UserRole.DISPATCHER]:
                return True 
            if obj_user == request.user: 
                return True

        return False