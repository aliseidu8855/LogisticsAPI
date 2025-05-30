# Generated by Django 5.2.1 on 2025-05-30 18:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('containers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='container',
            name='assigned_customer',
            field=models.ForeignKey(blank=True, limit_choices_to={'role': 'CU'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_containers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='container',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_containers', to=settings.AUTH_USER_MODEL),
        ),
    ]
