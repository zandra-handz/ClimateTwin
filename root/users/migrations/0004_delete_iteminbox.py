# Generated by Django 5.0.1 on 2024-02-03 02:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_iteminbox_items_delete_treasure'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ItemInbox',
        ),
    ]
