from rest_framework import serializers
from .models import ActionLog
from apps.users.serializers import UserSimpleSerializer 

class ActionLogSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    related_object_str = serializers.SerializerMethodField(read_only=True)
    content_type_str = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ActionLog
        fields = (
            'id', 'user', 'action_verb', 'content_type_str', 'object_id',
            'related_object_str', 'details', 'ip_address', 'timestamp'
        )
        read_only_fields = fields 

    def get_related_object_str(self, obj):
        return str(obj.related_object) if obj.related_object else None

    def get_content_type_str(self, obj):
        return obj.content_type.model if obj.content_type else None