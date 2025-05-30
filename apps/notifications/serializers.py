# apps/notifications/serializers.py
from rest_framework import serializers
from .models import Notification
from apps.users.serializers import UserSimpleSerializer 

class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserSimpleSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id', 'recipient', 'title', 'message', 'channel', 'channel_display',
            'status', 'status_display', 'related_object_info',
            'action_url', 'created_at', 'read_at', 'sent_at'
        )
        read_only_fields = (
            'id', 'recipient', 'title', 'message', 'channel', 'channel_display',
            'status_display', 'related_object_info', 'action_url',
            'created_at', 'sent_at'
        ) 

    related_object_info = serializers.SerializerMethodField()

    def get_related_object_info(self, obj):
        if obj.related_object:
            return {
                'type': obj.content_type.model,
                'id': obj.object_id,
                'str': str(obj.related_object)
            }
        return None