# Generated by Django 5.0.2 on 2025-03-28 22:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_remove_userprofile_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='treasure',
            name='finder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='found_treasures', to=settings.AUTH_USER_MODEL),
        ),
    ]
