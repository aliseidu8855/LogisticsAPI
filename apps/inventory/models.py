from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.containers.models import Container


class Supplier(models.Model):
    name = models.CharField(_("supplier name"), max_length=255, unique=True)
    contact_person = models.CharField(_("contact person"), max_length=255, blank=True)
    email = models.EmailField(_("email address"), unique=True)
    phone = models.CharField(_("phone number"), max_length=20, blank=True)
    address = models.TextField(_("address"), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_suppliers",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("created by"),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("supplier")
        verbose_name_plural = _("suppliers")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField(_("warehouse name"), max_length=255, unique=True)
    location_address = models.TextField(_("location address"))
    contact_email = models.EmailField(_("contact email"), blank=True)
    contact_phone = models.CharField(_("contact phone"), max_length=20, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_warehouses",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("created by"),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("warehouse")
        verbose_name_plural = _("warehouses")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(_("product name"), max_length=255)
    sku = models.CharField(_("SKU (Stock Keeping Unit)"), max_length=100, unique=True)
    description = models.TextField(_("description"), blank=True)
    cost_price = models.DecimalField(
        _("cost price"), max_digits=10, decimal_places=2, default=0.00
    )
    selling_price = models.DecimalField(
        _("selling price"), max_digits=10, decimal_places=2, default=0.00   
    )
    
    supplier = models.ForeignKey(
        Supplier,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("supplier"),
    )

    container = models.ForeignKey(
        Container,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("container"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("created by"),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["name", "sku"]

    def __str__(self):
        return f"{self.name} ({self.sku})"


class ProductStock(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="stock_levels",
        on_delete=models.CASCADE,
        verbose_name=_("product"),
    )
    warehouse = models.ForeignKey(
        Warehouse,
        related_name="products_stocked",
        on_delete=models.CASCADE,
        verbose_name=_("warehouse"),
    )
    quantity = models.PositiveIntegerField(_("quantity"), default=0)
    last_updated = models.DateTimeField(_("last updated"), auto_now=True)

    class Meta:
        verbose_name = _("product stock")
        verbose_name_plural = _("product stocks")
        unique_together = ("product", "warehouse")
        ordering = ["warehouse", "product"]

    def __str__(self):
        return f"{self.product.name} in {self.warehouse.name}: {self.quantity}"


class ProductTransferLog(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, verbose_name=_("product")
    )
    quantity = models.PositiveIntegerField(_("quantity transferred"))
    from_warehouse = models.ForeignKey(
        Warehouse,
        related_name="transfers_out",
        on_delete=models.PROTECT,
        verbose_name=_("from warehouse"),
    )
    to_warehouse = models.ForeignKey(
        Warehouse,
        related_name="transfers_in",
        on_delete=models.PROTECT,
        verbose_name=_("to warehouse"),
    )
    transferred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("transferred by"),
    )
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("product transfer log")
        verbose_name_plural = _("product transfer logs")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.quantity} of {self.product.sku} from {self.from_warehouse.name} to {self.to_warehouse.name} at {self.timestamp}"
