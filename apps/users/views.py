# apps/users/views.py
from django.contrib.auth import get_user_model
from django.db import models
from rest_framework import serializers
from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    UserRegistrationSerializer,
    UserDetailSerializer,
    ChangePasswordSerializer,
)
from .permissions import CanManageUser, IsOwnerOrAdminOrSuperuser
from .models import UserRole
from django.contrib.auth import logout as django_logout

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("email")
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, CanManageUser]

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        if self.action == "change_password_action":
            return ChangePasswordSerializer
        return UserDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            if getattr(self, 'swagger_fake_view', False):
                return User.objects.none() 
            return User.objects.none()
        if user.is_superuser or user.role == UserRole.ADMIN:
            return User.objects.all().order_by("email")
        elif user.role == UserRole.WAREHOUSE_MANAGER:
            return User.objects.filter(
                models.Q(role=UserRole.CUSTOMER)
                | models.Q(role=UserRole.DISPATCHER)
                | models.Q(id=user.id)
            ).order_by("email")
        return User.objects.filter(id=user.id)

    @action(
        detail=False,
        methods=["get", "put", "patch"],
        url_path="me",
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        user = request.user
        if request.method == "GET":
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)
        elif request.method in ["PUT", "PATCH"]:
            partial = request.method == "PATCH"
            serializer = UserDetailSerializer(
                user, data=request.data, partial=partial, context={"request": request}
            )
            if not (request.user.is_superuser or request.user.role == UserRole.ADMIN):
                if "role" in request.data:
                    return Response(
                        {"error": "You cannot change your role."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                if "email" in request.data and request.data["email"] != user.email:
                    return Response(
                        {"error": "You cannot change your email address here."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=["post"],
        url_path="change-password",
        permission_classes=[IsAuthenticated, IsOwnerOrAdminOrSuperuser],
    )
    def change_password_action(self, request, pk=None):
        user = self.get_object()
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request, "user_to_change": user}
        )
        if serializer.is_valid():
            if user != request.user and not (
                request.user.is_superuser or request.user.role == UserRole.ADMIN
            ):
                return Response(
                    {"error": "You can only change your own password."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if user == request.user:
                serializer.save()
                return Response(
                    {"detail": "Password changed successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                user.set_password(serializer.validated_data["new_password"])
                user.save()
                return Response(
                    {
                        "detail": f"Password for {user.email} changed successfully by admin."
                    },
                    status=status.HTTP_200_OK,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        requesting_user = self.request.user
        role_to_assign = serializer.validated_data.get("role", UserRole.CUSTOMER)

        if requesting_user.role == UserRole.WAREHOUSE_MANAGER:
            if role_to_assign not in [UserRole.CUSTOMER, UserRole.DISPATCHER]:
                raise serializers.ValidationError(
                    {
                        "role": f"Warehouse Managers can only create Customers or Dispatchers. "
                        f"Cannot create {UserRole(role_to_assign).label}."
                    }
                )
        elif not (
            requesting_user.is_superuser or requesting_user.role == UserRole.ADMIN
        ):
            if role_to_assign != UserRole.CUSTOMER:
                raise serializers.ValidationError(
                    {"role": "You do not have permission to assign this role."}
                )

        serializer.save()


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        django_logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
