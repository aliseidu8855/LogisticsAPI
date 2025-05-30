# apps/shipments/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.users.models import UserRole # For limit_choices_to

class Shipment(models.Model):
    class ShipmentStatus(models.TextChoices):
        PENDING_CONFIRMATION = 'PC', _('Pending Confirmation') 
        PROCESSING = 'PR', _('Processing') 
        AWAITING_PICKUP = 'AP', _('Awaiting Pickup') 
        SHIPPED = 'SH', _('Shipped') 
        IN_TRANSIT = 'IT', _('In Transit')
        ARRIVED_HUB = 'AH', _('Arrived at Hub/Port') 
        CUSTOMS_CLEARANCE = 'CC', _('Customs Clearance')
        OUT_FOR_DELIVERY = 'OD', _('Out for Local Delivery')
        DELIVERED = 'DE', _('Delivered')
        DELAYED = 'DL', _('Delayed')
        CANCELLED = 'CA', _('Cancelled')
        PARTIALLY_DELIVERED = 'PD', _('Partially Delivered') 

    shipment_tracking_id = models.CharField(
        _("shipment tracking ID"),
        max_length=100,
        unique=True,
        blank=True 
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='shipments',
        on_delete=models.PROTECT, 
        limit_choices_to={'role': UserRole.CUSTOMER},
        verbose_name=_("customer")
    )
    container = models.OneToOneField(
        'containers.Container', 
        related_name='shipment',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("container")
    )
    origin_warehouse = models.ForeignKey(
        'inventory.Warehouse', 
        related_name='shipments_originated',
        on_delete=models.PROTECT, 
        verbose_name=_("origin warehouse")
    )
    destination_address = models.TextField(_("destination address"))
    status = models.CharField(
        _("status"),
        max_length=2,
        choices=ShipmentStatus.choices,
        default=ShipmentStatus.PENDING_CONFIRMATION
    )
    estimated_departure_date = models.DateTimeField(_("estimated departure date"), null=True, blank=True)
    actual_departure_date = models.DateTimeField(_("actual departure date"), null=True, blank=True)
    estimated_delivery_date = models.DateTimeField(_("estimated delivery date"), null=True, blank=True)
    actual_delivery_date = models.DateTimeField(_("actual delivery date"), null=True, blank=True)
    notes = models.TextField(_("internal notes"), blank=True) # For WM/Dispatcher
    customer_notes = models.TextField(_("notes for customer"), blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_shipments',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("created by")
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("shipment")
        verbose_name_plural = _("shipments")
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.shipment_tracking_id:
            self.shipment_tracking_id = f"SHP-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.shipment_tracking_id} for {self.customer.email}"

class ShipmentItem(models.Model):
    shipment = models.ForeignKey(
        Shipment,
        related_name='items',
        on_delete=models.CASCADE, 
        verbose_name=_("shipment")
    )
    product = models.ForeignKey(
        'inventory.Product', 
        related_name='shipment_items',
        on_delete=models.PROTECT,
        verbose_name=_("product")
    )
    quantity = models.PositiveIntegerField(_("quantity"))


    class Meta:
        verbose_name = _("shipment item")
        verbose_name_plural = _("shipment items")
        unique_together = ('shipment', 'product') 

    def __str__(self):
        return f"{self.quantity} of {self.product.sku} for {self.shipment.shipment_tracking_id}"