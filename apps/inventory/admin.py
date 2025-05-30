from django.contrib import admin
from .models import Supplier, Warehouse, Product, ProductStock, ProductTransferLog

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'contact_person', 'created_by', 'created_at')
    search_fields = ('name', 'email', 'contact_person')
    list_filter = ('created_at',)
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not obj.pk: 
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_address', 'contact_email', 'created_by', 'created_at')
    search_fields = ('name', 'location_address')
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'supplier', 'created_by', 'created_at')
    search_fields = ('name', 'sku')
    list_filter = ('supplier', 'created_at')
    autocomplete_fields = ['supplier']
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity', 'last_updated')
    search_fields = ('product__name', 'product__sku', 'warehouse__name')
    list_filter = ('warehouse', 'last_updated')
    autocomplete_fields = ['product', 'warehouse']
    readonly_fields = ('last_updated',)

@admin.register(ProductTransferLog)
class ProductTransferLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'from_warehouse', 'to_warehouse', 'transferred_by', 'timestamp')
    search_fields = ('product__sku', 'from_warehouse__name', 'to_warehouse__name', 'transferred_by__email')
    list_filter = ('timestamp', 'transferred_by', 'from_warehouse', 'to_warehouse')
    readonly_fields = ('product', 'quantity', 'from_warehouse', 'to_warehouse', 'transferred_by', 'timestamp', 'notes')
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request): 
        return False
    def has_change_permission(self, request, obj=None):
        return False