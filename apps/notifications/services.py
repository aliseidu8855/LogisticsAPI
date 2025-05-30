# apps/notifications/services.py
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.conf import settings

from .models import Notification, NotificationChannel, NotificationStatus

# from config.celery import app as celery_app # If using Celery for dispatching


# @celery_app.task(name="dispatch_notification_task") # Example Celery task decorator
def dispatch_notification_task(notification_id):
    """
    Worker task to send a single notification.
    This would be called by Celery or a similar task queue.
    """
    try:
        notification = Notification.objects.get(
            id=notification_id, status=NotificationStatus.PENDING
        )
    except Notification.DoesNotExist:
        print(f"Notification {notification_id} not found or not pending for dispatch.")
        return False

    print(
        f"Dispatching notification ID {notification.id} for {notification.recipient} via {notification.channel}"
    )
    sent_successfully = False
    failure_reason = ""

    try:
        if notification.channel == NotificationChannel.EMAIL:
            subject = notification.title or "Logistics Platform Notification"
            from_email = settings.DEFAULT_FROM_EMAIL or "noreply@example.com"
            recipient_list = [notification.recipient.email]

            send_mail(
                subject,
                notification.message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
            sent_successfully = True
            print(f"Email sent to {notification.recipient.email}")

        elif notification.channel == NotificationChannel.PUSH:
            print(
                f"Simulating PUSH notification to {notification.recipient.username}: {notification.title}"
            )
            sent_successfully = True

        elif notification.channel == NotificationChannel.IN_APP:

            sent_successfully = True
            print(
                f"In-App notification {notification.id} made available for {notification.recipient.username}"
            )

    except Exception as e:
        print(f"Failed to send notification {notification.id}: {e}")
        failure_reason = str(e)
        sent_successfully = False

    if sent_successfully:
        notification.mark_as_sent()
    else:
        notification.mark_as_failed(reason=failure_reason)
    return sent_successfully


def create_notification(
    recipient,
    message,
    title="",
    channel=NotificationChannel.EMAIL,
    related_object=None,
    action_url=None,
    send_async=True,
):
    """
    Creates a notification record and optionally triggers its dispatch.
    """
    content_type = None
    object_id = None
    if related_object:
        content_type = ContentType.objects.get_for_model(related_object)
        object_id = related_object.pk

    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        channel=channel,
        status=NotificationStatus.PENDING,
        content_type=content_type,
        object_id=object_id,
        action_url=action_url,
    )

    if send_async and settings.CELERY_BROKER_URL:  #
        print(
            f"Notification {notification.id} queued for asynchronous dispatch (Celery)."
        )

        if not getattr(settings, "CELERY_WORKER_RUNNING", False):
            dispatch_notification_task(notification.id)
    elif not send_async:
        dispatch_notification_task(notification.id)
    else:
        print(
            f"Notification {notification.id} created. Celery not configured or send_async=False but no direct call."
        )

    return notification
