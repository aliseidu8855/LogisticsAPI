from django.contrib import admin
from .models import Container, ContainerCodeSequence


@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    list_display = (
        "container_id_code",
        "type",
        "status",
        "current_warehouse",
        "current_location_description",
        "created_by",
        "updated_at",
    )
    list_filter = ("status", "type", "current_warehouse", "created_at")
    search_fields = (
        "container_id_code",
        "current_location_description",
        "created_by__email",
        "current_warehouse__name",
    )
    autocomplete_fields = ["current_warehouse", "created_by"]
    readonly_fields = ("container_id_code", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("container_id_code", "type", "status")}),
        (
            "Location Details",
            {"fields": ("current_location_description", "current_warehouse")},
        ),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ContainerCodeSequence)
class ContainerCodeSequenceAdmin(admin.ModelAdmin):
    list_display = ("id", "current_number")

    def has_add_permission(self, request):
        return not ContainerCodeSequence.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False  # Don't allow deletion
