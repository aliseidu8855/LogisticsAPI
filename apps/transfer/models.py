from django.db import models
from apps.inventory.models import Product
from apps.inventory.models import Warehouse
from apps.users.models import User
from django.utils.translation import gettext_lazy as _

class ProductTransferLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transfer_logs', verbose_name=_("product"))
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='transfer_logs_from', verbose_name=_("from warehouse"))
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='transfer_logs_to', verbose_name=_("to warehouse"))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_transfer_logs', verbose_name=_("created by"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("product transfer log")
        verbose_name_plural = _("product transfer logs")
        ordering = ['-created_at']

    def __str__(self):
        return f"Transfer of {self.quantity} {self.product.name} from {self.from_warehouse.name} to {self.to_warehouse.name}"