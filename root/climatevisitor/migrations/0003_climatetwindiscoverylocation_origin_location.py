# Generated by Django 5.0.1 on 2024-01-30 00:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatevisitor', '0002_rename_wind_agreement_score_climatetwinlocation_cloudiness_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='climatetwindiscoverylocation',
            name='origin_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='climatevisitor.climatetwinlocation'),
        ),
    ]
