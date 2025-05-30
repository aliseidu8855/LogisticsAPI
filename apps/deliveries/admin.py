# apps/deliveries/admin.py
from django.contrib import admin
from .models import DeliveryTask

@admin.register(DeliveryTask)
class DeliveryTaskAdmin(admin.ModelAdmin):
    list_display = (
        'shipment_tracking_id_link', 'dispatcher', 'status',
        'scheduled_pickup_datetime', 'scheduled_delivery_datetime', 'updated_at'
    )
    list_filter = ('status', 'dispatcher', 'scheduled_pickup_datetime', 'scheduled_delivery_datetime')
    search_fields = (
        'shipment__shipment_tracking_id', 'dispatcher__email',
        'pickup_address_override', 'delivery_address_override'
    )
    autocomplete_fields = ['shipment', 'dispatcher']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('shipment', 'dispatcher', 'status')
        }),
        ('Pickup Details', {
            'fields': ('pickup_address_override', 'scheduled_pickup_datetime', 'actual_pickup_datetime')
        }),
        ('Delivery Details', {
            'fields': ('delivery_address_override', 'scheduled_delivery_datetime', 'actual_delivery_datetime')
        }),
        ('Proof of Delivery', {
            'fields': ('recipient_name', 'signature_data'), 
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('dispatcher_notes', 'internal_notes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def shipment_tracking_id_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.shipment:
            link = reverse("admin:shipments_shipment_change", args=[obj.shipment.id])
            return format_html('<a href="{}">{}</a>', link, obj.shipment.shipment_tracking_id)
        return "N/A"
    shipment_tracking_id_link.short_description = 'Shipment Tracking ID'
