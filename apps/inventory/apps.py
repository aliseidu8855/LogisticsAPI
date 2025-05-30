from django.apps import AppConfig

class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory'

    def ready(self):
        try:
            import apps.inventory.signals  # noqa F401
        except ImportError:
            pass