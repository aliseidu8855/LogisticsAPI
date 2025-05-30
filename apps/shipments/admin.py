# apps/shipments/admin.py
from django.contrib import admin
from .models import Shipment, ShipmentItem

class ShipmentItemInline(admin.TabularInline): 
    model = ShipmentItem
    extra = 1 
    autocomplete_fields = ['product']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        'shipment_tracking_id', 'customer', 'status', 'origin_warehouse',
        'container', 'estimated_delivery_date', 'created_by', 'updated_at'
    )
    list_filter = ('status', 'origin_warehouse', 'customer', 'created_at', 'estimated_delivery_date')
    search_fields = (
        'shipment_tracking_id', 'customer__email', 'customer__first_name', 'customer__last_name',
        'container__container_id_code', 'destination_address'
    )
    autocomplete_fields = ['customer', 'container', 'origin_warehouse', 'created_by']
    readonly_fields = ('shipment_tracking_id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [ShipmentItemInline]

    fieldsets = (
        (None, {
            'fields': ('shipment_tracking_id', 'customer', 'status')
        }),
        ('Origin & Destination', {
            'fields': ('origin_warehouse', 'destination_address')
        }),
        ('Container & Dates', {
            'fields': ('container', 'estimated_departure_date', 'actual_departure_date',
                       'estimated_delivery_date', 'actual_delivery_date')
        }),
        ('Notes', {
            'fields': ('notes', 'customer_notes')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk: 
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)

@admin.register(ShipmentItem)
class ShipmentItemAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'product', 'quantity')
    search_fields = ('shipment__shipment_tracking_id', 'product__name', 'product__sku')
    autocomplete_fields = ['shipment', 'product']
