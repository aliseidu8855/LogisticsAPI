from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
import json
from .models import ActionLog

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 'user_display', 'action_verb',
        'related_object_link', 'ip_address', 'details_preview'
    )
    list_filter = ('action_verb', 'timestamp', 'user', 'content_type')
    search_fields = ('user__email', 'action_verb', 'details', 'ip_address', 'object_id')
    readonly_fields = (
        'timestamp', 'user', 'action_verb', 'content_type',
        'object_id', 'related_object', 'details', 'ip_address'
    )
    date_hierarchy = 'timestamp'

    fieldsets = (
        (None, {'fields': ('timestamp', 'user', 'action_verb', 'ip_address')}),
        ('Related Object', {'fields': ('content_type', 'object_id', 'related_object')}),
        ('Details', {'fields': ('details',)}),
    )

    def user_display(self, obj):
        return obj.user.email if obj.user else "System/Anonymous"
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__email'

    def related_object_link(self, obj):
        if obj.related_object and obj.content_type:
            try:
                app_label = obj.content_type.app_label
                model_name = obj.content_type.model
                link_url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.object_id])
                return format_html('<a href="{}">{} ({})</a>', link_url, obj.related_object, model_name.capitalize())
            except Exception: 
                return f"{obj.related_object} ({obj.content_type.model.capitalize() if obj.content_type else 'N/A'})"
        return "-"
    related_object_link.short_description = 'Related Object'

    def details_preview(self, obj):
        if obj.details:
            try:
                pretty_details = json.dumps(obj.details, indent=2)
                preview = (pretty_details[:200] + '...') if len(pretty_details) > 200 else pretty_details
                return format_html("<pre style='white-space: pre-wrap; word-break: break-all;'>{}</pre>", preview)
            except TypeError:
                return str(obj.details)[:200] 
        return "-"
    details_preview.short_description = 'Details (Preview)'

    def has_add_permission(self, request): 
        return False
    def has_change_permission(self, request, obj=None): 
        return False
