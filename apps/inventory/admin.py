from django.contrib import admin
from .models import Supplier, Warehouse, Product


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
        "contact_person",
        "created_by",
        "created_at",
    )
    search_fields = ("name", "email", "contact_person")
    list_filter = ("created_at",)
    readonly_fields = ("created_by", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "location_address",
        "contact_email",
        "created_by",
        "created_at",
    )
    search_fields = ("name", "location_address")
    readonly_fields = ("created_by", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "supplier",
        "container",
        "created_by",
        "created_at",
    )
    search_fields = ("name", "supplier__name", "container__name")
    list_filter = ("created_at", "supplier")
    readonly_fields = ("created_by", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)



