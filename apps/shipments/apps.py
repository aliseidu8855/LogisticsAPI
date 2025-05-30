# apps/shipments/apps.py
from django.apps import AppConfig

class ShipmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shipments'

    def ready(self):
        try:
            import apps.shipments.signals  # noqa F401
        except ImportError:
            pass