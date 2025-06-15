from django.db import models, transaction
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ContainerCodeSequence(models.Model):
    current_number = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Container Code Sequence")
        verbose_name_plural = _("Container Code Sequences")

    @classmethod
    def get_next_number(cls):
        with transaction.atomic():
            sequence, created = cls.objects.select_for_update().get_or_create(pk=1)
            sequence.current_number += 1
            sequence.save()
            return sequence.current_number


class Container(models.Model):
    class ContainerStatus(models.TextChoices):
        EMPTY = "EM", _("Empty")
        AVAILABLE = "AV", _("Available")
        LOADING = "LO", _("Loading")
        LOADED = "LD", _("Loaded")
        IN_TRANSIT_TO_PORT = "TP", _("In Transit to Port/Hub")
        AT_PORT_ORIGIN = "AP", _("At Port/Hub of Origin")
        IN_TRANSIT_MAIN = "IT", _("In Transit (Main Leg)")
        AT_PORT_DESTINATION = "AD", _("At Port/Hub of Destination")
        IN_TRANSIT_TO_CUSTOMER = "TC", _("In Transit to Customer/Warehouse")
        UNLOADING = "UL", _("Unloading")
        AWAITING_RETURN = "AR", _("Awaiting Return")
        IN_TRANSIT_RETURN = "TR", _("In Transit (Return)")
        MAINTENANCE = "MA", _("Under Maintenance")
        DAMAGED = "DA", _("Damaged")
        DECOMMISSIONED = "DE", _("Decommissioned")

    container_id_code = models.CharField(
        _("container ID code"),
        max_length=50,
        unique=True,
        help_text=_("e.g., #C-00001"),
        blank=True,
    )
    type = models.CharField(
        _("container type"),
        max_length=100,
        help_text=_("e.g., 20ft Dry Standard, 40ft High Cube, Reefer"),
    )
    status = models.CharField(
        _("status"),
        max_length=2,
        choices=ContainerStatus.choices,
        default=ContainerStatus.AVAILABLE,
    )
    current_location_description = models.CharField(
        _("current location description"),
        max_length=255,
        blank=True,
        help_text=_("Free text for current location, e.g., 'Port of LA, Berth 5'"),
    )
    current_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="containers_at_warehouse",
        verbose_name=_("current warehouse"),
    )
    current_goods_description = models.TextField(
        _("current goods description"),
        blank=True,
        help_text=_(
            "Brief description of goods currently or last loaded, if tracked directly on container."
        ),
    )
    last_known_origin = models.CharField(
        _("last known origin"),
        max_length=255,
        blank=True,
        help_text=_(
            "Origin port/city of its last significant journey, if tracked directly."
        ),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_containers",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("created by"),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("container")
        verbose_name_plural = _("containers")
        ordering = ["-updated_at", "container_id_code"]

    def save(self, *args, **kwargs):
        if not self.container_id_code:
            next_number = ContainerCodeSequence.get_next_number()
            self.container_id_code = f"#C-{next_number:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.container_id_code} ({self.get_status_display()})"
