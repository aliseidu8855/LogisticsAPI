# Generated by Django 5.2.1 on 2025-06-15 04:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shipments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PA', 'Pending Assignment'), ('AS', 'Assigned to Dispatcher'), ('WP', 'Awaiting Pickup by Dispatcher'), ('PU', 'Picked Up from Origin'), ('IT', 'In Transit (Local Delivery)'), ('AC', 'Arrived at Customer Location'), ('DE', 'Delivered'), ('FD', 'Failed Delivery Attempt'), ('RS', 'Rescheduled'), ('RH', 'Returning to Hub/Warehouse'), ('RT', 'Returned to Hub/Warehouse'), ('CA', 'Cancelled')], default='PA', max_length=2, verbose_name='status')),
                ('pickup_address_override', models.TextField(blank=True, help_text='If different from shipment origin.', verbose_name='pickup address override')),
                ('scheduled_pickup_datetime', models.DateTimeField(blank=True, null=True, verbose_name='scheduled pickup datetime')),
                ('actual_pickup_datetime', models.DateTimeField(blank=True, null=True, verbose_name='actual pickup datetime')),
                ('delivery_address_override', models.TextField(blank=True, help_text='If different from shipment destination.', verbose_name='delivery address override')),
                ('scheduled_delivery_datetime', models.DateTimeField(blank=True, null=True, verbose_name='scheduled delivery datetime')),
                ('actual_delivery_datetime', models.DateTimeField(blank=True, null=True, verbose_name='actual delivery datetime')),
                ('recipient_name', models.CharField(blank=True, max_length=255, verbose_name='recipient name')),
                ('signature_data', models.TextField(blank=True, verbose_name='signature data (e.g., base64 image)')),
                ('dispatcher_notes', models.TextField(blank=True, verbose_name='dispatcher notes')),
                ('internal_notes', models.TextField(blank=True, verbose_name='internal notes')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('dispatcher', models.ForeignKey(blank=True, limit_choices_to={'role': 'DI'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='delivery_tasks', to=settings.AUTH_USER_MODEL, verbose_name='dispatcher')),
                ('shipment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_task', to='shipments.shipment', verbose_name='shipment')),
            ],
            options={
                'verbose_name': 'delivery task',
                'verbose_name_plural': 'delivery tasks',
                'ordering': ['-created_at'],
            },
        ),
    ]
