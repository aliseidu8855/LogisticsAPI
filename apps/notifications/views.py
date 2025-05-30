# apps/notifications/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet): 
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This viewset should only return notifications for the currently authenticated user.
        """
        user = self.request.user
        return Notification.objects.filter(
            recipient=user
        ).exclude(
            status=Notification.NotificationStatus.ARCHIVED
        ).select_related('recipient', 'content_type').order_by('-created_at')

    @action(detail=True, methods=['post'], url_path='mark-as-read')
    def mark_as_read_action(self, request, pk=None):
        notification = self.get_object()
        if notification.recipient != request.user:
            return Response({"detail": "Not your notification."}, status=status.HTTP_403_FORBIDDEN)

        notification.mark_as_read()
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'], url_path='mark-all-as-read')
    def mark_all_as_read_action(self, request):
        updated_count = Notification.objects.filter(
            recipient=request.user,
            status__in=[Notification.NotificationStatus.SENT, Notification.NotificationStatus.PENDING] 
        ).update(status=Notification.NotificationStatus.READ, read_at=timezone.now())
        return Response({"detail": f"{updated_count} notifications marked as read."})
