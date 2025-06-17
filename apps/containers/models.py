from django.db import models, transaction
from django.db.models import Sum, F, DecimalField
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from decimal import Decimal  


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

    def calculate_purchased_cost(self):
        """
        Calculate the sum of the cost_of_product for all products in this container.
        Ensures the return type is Decimal.
        """
        aggregation = self.products.aggregate(total_cost=Sum("cost_of_product"))
        total_cost_value = aggregation["total_cost"]
        if total_cost_value is None:
            return Decimal("0.00")
        # Explicitly convert to Decimal, handling potential float from aggregation
        return Decimal(str(total_cost_value))

    def calculate_expected_revenue(self):
        """
        Calculate the sum of the selling_cost for all products in this container.
        Ensures the return type is Decimal.
        """
        aggregation = self.products.aggregate(total_revenue=Sum("selling_cost"))
        total_revenue_value = aggregation["total_revenue"]
        if total_revenue_value is None:
            return Decimal("0.00")
        return Decimal(str(total_revenue_value))

    bank_charges = models.DecimalField(
        _("bank charges"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Bank charges of the container."),
    )
    duty_and_ag_fess = models.DecimalField(
        _("duty and AG fees"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("duty and AG fees of the container."),
    )
    transportation_fees = models.DecimalField(
        _("Transportation fees"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Transport of the container."),
    )
    discharge = models.DecimalField(
        _("discharges"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("discharge of the container."),
    )


    def expected_profit(self):
        """
        Calculate the expected profit for the container.
        All monetary values are handled as Decimals.
        """
        purchased_cost = self.calculate_purchased_cost()  
        expected_revenue = self.calculate_expected_revenue()  
        bank_charges = Decimal(str(self.bank_charges)) if self.bank_charges is not None else Decimal("0.00")
        duty_and_ag_fees_val = self.duty_and_ag_fess  
        duty_and_ag_fees = Decimal(str(duty_and_ag_fees_val)) if duty_and_ag_fees_val is not None else Decimal(
            "0.00"
        )
        transportation_fees = Decimal(str(self.transportation_fees)) if self.transportation_fees is not None else Decimal(
            "0.00"
        )
        discharge = Decimal(str(self.discharge)) if self.discharge is not None else Decimal("0.00")
        cost_of_goods = purchased_cost + bank_charges + duty_and_ag_fees + transportation_fees + discharge
        return expected_revenue - cost_of_goods

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

    # def save(self, *args, **kwargs):
    #     if not self.container_id_code:
    #         next_number = ContainerCodeSequence.get_next_number()
    #         self.container_id_code = f"#C-{next_number:05d}"
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.container_id_code} ({self.get_status_display()})"
