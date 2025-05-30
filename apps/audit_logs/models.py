from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

class ActionLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        verbose_name=_("user")
    )
    action_verb = models.CharField(
        _("action verb"),
        max_length=255,
        help_text=_("A code representing the action, e.g., PRODUCT_CREATED, SHIPMENT_STATUS_UPDATED")
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        verbose_name=_("content type")
    )
    object_id = models.PositiveIntegerField(_("object ID"), null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    details = models.JSONField(
        _("details"),
        null=True, blank=True,
        help_text=_("Contextual data about the action, e.g., old/new values, parameters")
    )
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)

    class Meta:
        verbose_name = _("action log")
        verbose_name_plural = _("action logs")
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.email if self.user else "System/Anonymous"
        action_on = f" on {self.related_object}" if self.related_object else ""
        return f"{user_str} performed {self.action_verb}{action_on} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"