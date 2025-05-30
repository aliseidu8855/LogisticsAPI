# apps/deliveries/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.users.models import UserRole
from apps.shipments.models import Shipment


class DeliveryTask(models.Model):
    class DeliveryStatus(models.TextChoices):
        PENDING_ASSIGNMENT = "PA", _("Pending Assignment")
        ASSIGNED = "AS", _("Assigned to Dispatcher")
        AWAITING_PICKUP = "WP", _("Awaiting Pickup by Dispatcher")
        PICKED_UP = "PU", _("Picked Up from Origin")
        IN_TRANSIT_LOCAL = "IT", _("In Transit (Local Delivery)")
        ARRIVED_CUSTOMER = "AC", _("Arrived at Customer Location")
        DELIVERED = "DE", _("Delivered")
        FAILED_DELIVERY_ATTEMPT = "FD", _("Failed Delivery Attempt")
        RESCHEDULED = "RS", _("Rescheduled")
        RETURN_TO_HUB = "RH", _("Returning to Hub/Warehouse")
        RETURNED = "RT", _("Returned to Hub/Warehouse")
        CANCELLED = "CA", _("Cancelled")

    shipment = models.OneToOneField(
        "shipments.Shipment",
        related_name="delivery_task",
        on_delete=models.CASCADE,
        verbose_name=_("shipment"),
    )
    dispatcher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="delivery_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": UserRole.DISPATCHER},
        verbose_name=_("dispatcher"),
    )
    status = models.CharField(
        _("status"),
        max_length=2,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING_ASSIGNMENT,
    )
    pickup_address_override = models.TextField(
        _("pickup address override"),
        blank=True,
        help_text=_("If different from shipment origin."),
    )
    scheduled_pickup_datetime = models.DateTimeField(
        _("scheduled pickup datetime"), null=True, blank=True
    )
    actual_pickup_datetime = models.DateTimeField(
        _("actual pickup datetime"), null=True, blank=True
    )

    delivery_address_override = models.TextField(
        _("delivery address override"),
        blank=True,
        help_text=_("If different from shipment destination."),
    )
    scheduled_delivery_datetime = models.DateTimeField(
        _("scheduled delivery datetime"), null=True, blank=True
    )
    actual_delivery_datetime = models.DateTimeField(
        _("actual delivery datetime"), null=True, blank=True
    )

    recipient_name = models.CharField(_("recipient name"), max_length=255, blank=True)
    signature_data = models.TextField(
        _("signature data (e.g., base64 image)"), blank=True
    )

    dispatcher_notes = models.TextField(_("dispatcher notes"), blank=True)
    internal_notes = models.TextField(_("internal notes"), blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("delivery task")
        verbose_name_plural = _("delivery tasks")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Delivery for {self.shipment.shipment_tracking_id} - {self.get_status_display()}"

    def get_pickup_address(self):
        return self.pickup_address_override or (
            self.shipment.origin_warehouse.location_address
            if self.shipment and self.shipment.origin_warehouse
            else "N/A"
        )

    def get_delivery_address(self):
        return self.delivery_address_override or (
            self.shipment.destination_address if self.shipment else "N/A"
        )

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_status = None
        if not is_new:
            try:
                old_status = DeliveryTask.objects.get(pk=self.pk).status
            except DeliveryTask.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if self.shipment:
            shipment_updated = False
            if (
                self.status == DeliveryTask.DeliveryStatus.PICKED_UP
                and self.shipment.status
                not in [
                    Shipment.ShipmentStatus.OUT_FOR_DELIVERY,
                    Shipment.ShipmentStatus.DELIVERED,
                ]
            ):  
                self.shipment.status = Shipment.ShipmentStatus.OUT_FOR_DELIVERY
                shipment_updated = True
            elif (
                self.status == DeliveryTask.DeliveryStatus.DELIVERED
                and self.shipment.status != Shipment.ShipmentStatus.DELIVERED
            ):
                self.shipment.status = Shipment.ShipmentStatus.DELIVERED
                if not self.shipment.actual_delivery_date:
                    self.shipment.actual_delivery_date = (
                        self.actual_delivery_datetime or timezone.now()
                    )
                shipment_updated = True

            if shipment_updated:
                self.shipment.save(
                    update_fields=(
                        ["status", "actual_delivery_date"]
                        if "actual_delivery_date" in self.shipment.__dict__
                        else ["status"]
                    )
                )
