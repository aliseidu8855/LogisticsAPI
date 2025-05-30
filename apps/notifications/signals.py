# apps/notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from apps.shipments.models import Shipment, ShipmentStatus
from apps.deliveries.models import DeliveryTask
from .services import create_notification
from .models import NotificationChannel


@receiver(post_save, sender=Shipment)
def shipment_status_change_notification(sender, instance: Shipment, created, **kwargs):
    """
    Send notification to customer when shipment status changes significantly.
    """
    if created:
        title = f"Shipment {instance.shipment_tracking_id} Confirmed"
        message = (
            f"Dear {instance.customer.first_name or instance.customer.email},\n\n"
            f"Your shipment with tracking ID {instance.shipment_tracking_id} has been confirmed and is now being processed.\n"
            f"Origin: {instance.origin_warehouse.name}\n"
            f"Destination: {instance.destination_address}\n\n"
            f"You can track its progress on our platform."
        )

        create_notification(
            recipient=instance.customer,
            title=title,
            message=message,
            channel=NotificationChannel.EMAIL,
            related_object=instance,
        )
        return

    if (
        "update_fields" in kwargs
        and kwargs["update_fields"]
        and "status" not in kwargs["update_fields"]
    ):
        return

    if instance.status == ShipmentStatus.SHIPPED:
        title = f"Shipment {instance.shipment_tracking_id} Has Shipped!"
        message = f"Good news! Your shipment {instance.shipment_tracking_id} has left {instance.origin_warehouse.name} and is on its way."
        create_notification(
            instance.customer, message, title=title, related_object=instance
        )

    elif instance.status == ShipmentStatus.OUT_FOR_DELIVERY:
        title = f"Shipment {instance.shipment_tracking_id} is Out for Delivery"
        message = f"Your shipment {instance.shipment_tracking_id} is out for local delivery today. Estimated delivery: {instance.estimated_delivery_date.strftime('%Y-%m-%d %H:%M') if instance.estimated_delivery_date else 'Today'}."
        create_notification(
            instance.customer, message, title=title, related_object=instance
        )

    elif instance.status == ShipmentStatus.DELIVERED:
        title = f"Shipment {instance.shipment_tracking_id} Delivered"
        message = f"Your shipment {instance.shipment_tracking_id} has been successfully delivered. Thank you for using our service!"
        create_notification(
            instance.customer, message, title=title, related_object=instance
        )

    elif instance.status == ShipmentStatus.DELAYED:
        title = f"Shipment {instance.shipment_tracking_id} Delayed"
        message = f"We're sorry, your shipment {instance.shipment_tracking_id} is experiencing a delay. Please check the platform for more details or contact support."
        create_notification(
            instance.customer, message, title=title, related_object=instance
        )


@receiver(post_save, sender=DeliveryTask)
def delivery_task_assignment_notification(
    sender, instance: DeliveryTask, created, **kwargs
):
    """
    Notify dispatcher when a task is assigned to them.
    """
    if instance.dispatcher and (
        created or ("dispatcher" in (kwargs.get("update_fields") or []))
    ):

        if (
            kwargs.get("update_fields")
            and "dispatcher" not in kwargs["update_fields"]
            and not created
        ):
            return

        title = f"New Delivery Task Assigned: {instance.shipment.shipment_tracking_id}"
        message = (
            f"Hello {instance.dispatcher.first_name or instance.dispatcher.email},\n\n"
            f"A new delivery task for shipment {instance.shipment.shipment_tracking_id} has been assigned to you.\n"
            f"Pickup from: {instance.get_pickup_address()}\n"
            f"Deliver to: {instance.get_delivery_address()}\n"
            f"Scheduled Delivery: {instance.scheduled_delivery_datetime.strftime('%Y-%m-%d %H:%M') if instance.scheduled_delivery_datetime else 'ASAP'}\n\n"
            f"Please check your task list on the platform."
        )
        create_notification(
            recipient=instance.dispatcher,
            title=title,
            message=message,
            channel=NotificationChannel.EMAIL,
            related_object=instance,
        )
