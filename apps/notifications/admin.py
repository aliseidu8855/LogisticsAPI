from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'recipient_email', 'title_preview', 'channel', 'status',
        'related_object_admin_link', 'created_at', 'read_at', 'sent_at'
    )
    list_filter = ('channel', 'status', 'created_at', 'recipient')
    search_fields = ('recipient__email', 'title', 'message')
    readonly_fields = (
        'recipient', 'title', 'message', 'channel', 'content_type', 'object_id',
        'related_object', 'action_url', 'created_at', 'sent_at', 'read_at'
    ) 
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {'fields': ('recipient', 'channel', 'status')}),
        ('Content', {'fields': ('title', 'message', 'action_url')}),
        ('Related Object', {'fields': ('content_type', 'object_id', 'related_object')}),
        ('Timestamps', {'fields': ('created_at', 'sent_at', 'read_at')}),
    )

    def recipient_email(self, obj):
        return obj.recipient.email
    recipient_email.short_description = 'Recipient'
    recipient_email.admin_order_field = 'recipient__email'

    def title_preview(self, obj):
        return obj.title[:75] + '...' if len(obj.title) > 75 else obj.title
    title_preview.short_description = 'Title'

    def related_object_admin_link(self, obj):
        if obj.related_object:
            from django.urls import reverse
            from django.utils.html import format_html
            try:
                link = reverse(f"admin:{obj.content_type.app_label}_{obj.content_type.model}_change", args=[obj.object_id])
                return format_html('<a href="{}">{} ({})</a>', link, obj.related_object, obj.content_type.model.capitalize())
            except Exception:
                return f"{obj.related_object} ({obj.content_type.model.capitalize()})"
        return "-"
    related_object_admin_link.short_description = 'Related Object'

