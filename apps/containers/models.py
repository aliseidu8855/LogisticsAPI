# apps/containers/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.users.models import UserRole

class Container(models.Model):
    class ContainerStatus(models.TextChoices):
        EMPTY = 'EM', _('Empty')
        AVAILABLE = 'AV', _('Available') 
        LOADING = 'LO', _('Loading')
        LOADED = 'LD', _('Loaded') 
        IN_TRANSIT_TO_PORT = 'TP', _('In Transit to Port/Hub')
        AT_PORT_ORIGIN = 'AP', _('At Port/Hub of Origin')
        IN_TRANSIT_MAIN = 'IT', _('In Transit (Main Leg)') 
        AT_PORT_DESTINATION = 'AD', _('At Port/Hub of Destination')
        IN_TRANSIT_TO_CUSTOMER = 'TC', _('In Transit to Customer')
        UNLOADING = 'UL', _('Unloading at Customer')
        AWAITING_RETURN = 'AR', _('Awaiting Return')
        IN_TRANSIT_RETURN = 'TR', _('In Transit (Return)')
        MAINTENANCE = 'MA', _('Under Maintenance')
        DAMAGED = 'DA', _('Damaged')
        DECOMMISSIONED = 'DE', _('Decommissioned')

    container_id_code = models.CharField(
        _("container ID code"),
        max_length=50,
        unique=True,
        help_text=_("e.g., MSKU1234567, a unique identifier for the container")
    )
    type = models.CharField(
        _("container type"),
        max_length=50,
        help_text=_("e.g., 20ft Dry, 40ft HC Reefer, 20ft Tank")
    )
    status = models.CharField(
        _("status"),
        max_length=2,
        choices=ContainerStatus.choices,
        default=ContainerStatus.AVAILABLE
    )
    current_location_description = models.CharField(
        _("current location description"),
        max_length=255,
        blank=True,
        help_text=_("e.g., Warehouse A, Port of LA, On Vessel Evergreen")
    )
    current_warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='containers_at_warehouse',
        verbose_name=_("current warehouse")
    )
    assigned_customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='assigned_containers',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': UserRole.CUSTOMER}, 
        verbose_name=_("assigned customer")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_containers',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("created by")
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("container")
        verbose_name_plural = _("containers")
        ordering = ['container_id_code']

    def __str__(self):
        return f"{self.container_id_code} ({self.get_status_display()})"