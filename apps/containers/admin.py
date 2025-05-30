from django.contrib import admin
from .models import Container

@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    list_display = (
        'container_id_code', 'type', 'status', 'current_warehouse',
        'assigned_customer', 'created_by', 'updated_at'
    )
    list_filter = ('status', 'type', 'current_warehouse', 'assigned_customer')
    search_fields = (
        'container_id_code', 'current_location_description',
        'assigned_customer__email', 'created_by__email'
    )
    autocomplete_fields = ['current_warehouse', 'assigned_customer', 'created_by']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('container_id_code', 'type', 'status')
        }),
        ('Location & Assignment', {
            'fields': ('current_location_description', 'current_warehouse', 'assigned_customer')
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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form