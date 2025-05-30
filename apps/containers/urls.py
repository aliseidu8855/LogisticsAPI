from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContainerViewSet

router = DefaultRouter()
router.register(r'', ContainerViewSet, basename='container')

urlpatterns = [
    path('', include(router.urls)),
]