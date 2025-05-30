from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Notification(models.Model):
    class NotificationChannel(models.TextChoices):
        EMAIL = 'EM', _('Email')
        PUSH = 'PU', _('Push Notification') 
        IN_APP = 'IA', _('In-App Message') 

    class NotificationStatus(models.TextChoices):
        PENDING = 'PE', _('Pending')
        SENT = 'SE', _('Sent')
        FAILED = 'FA', _('Failed')
        READ = 'RD', _('Read')
        ARCHIVED = 'AR', _('Archived')

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        on_delete=models.CASCADE,
        verbose_name=_("recipient")
    )
    title = models.CharField(_("title"), max_length=255, blank=True)
    message = models.TextField(_("message"))
    channel = models.CharField(
        _("channel"),
        max_length=2,
        choices=NotificationChannel.choices,
        default=NotificationChannel.EMAIL
    )
    status = models.CharField(
        _("status"),
        max_length=2,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name=_("content type")
    )
    object_id = models.PositiveIntegerField(_("object ID"), null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    action_url = models.URLField(_("action URL"), blank=True, null=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    sent_at = models.DateTimeField(_("sent at"), null=True, blank=True)
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.email} ({self.get_channel_display()}) - {self.title[:50]}"

    def mark_as_read(self):
        if not self.read_at:
            self.status = Notification.NotificationStatus.READ
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at'])

    def mark_as_sent(self):
        self.status = Notification.NotificationStatus.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])

    def mark_as_failed(self, reason=""):
        self.status = Notification.NotificationStatus.FAILED

        self.save(update_fields=['status']) 