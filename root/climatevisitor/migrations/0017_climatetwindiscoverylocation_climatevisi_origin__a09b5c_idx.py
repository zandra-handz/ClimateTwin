# Generated by Django 5.0.2 on 2025-02-14 01:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatevisitor', '0016_climatetwinexplorelocation_climatevisi_created_212e42_idx_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='climatetwindiscoverylocation',
            index=models.Index(fields=['origin_location'], name='climatevisi_origin__a09b5c_idx'),
        ),
    ]
