from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryTaskViewSet

router = DefaultRouter()
router.register(r'tasks', DeliveryTaskViewSet, basename='deliverytask') # /api/deliveries/tasks/

urlpatterns = [
    path('', include(router.urls)),
]