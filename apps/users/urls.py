# apps/users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, UserViewSet
from rest_framework import permissions



router = DefaultRouter()
router.register(r'', UserViewSet, basename='user') # /api/users/, /api/users/{id}/, /api/users/me/

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('', include(router.urls)),
    # The /me/ and /change-password/ actions are part of the UserViewSet router
]