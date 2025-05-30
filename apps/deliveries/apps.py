# apps/deliveries/apps.py
from django.apps import AppConfig

class DeliveriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.deliveries'

    def ready(self):
        try:
            import apps.deliveries.signals  # noqa F401
        except ImportError:
            pass