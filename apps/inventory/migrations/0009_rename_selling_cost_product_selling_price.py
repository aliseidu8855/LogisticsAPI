# Generated by Django 5.2.3 on 2025-06-17 19:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_rename_quantity_producttransferlog_quantity_transferred_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='selling_cost',
            new_name='selling_price',
        ),
    ]
