# Generated by Django 5.0.2 on 2025-04-19 19:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatevisitor', '0022_currentlocation_base_location'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchivedDiscoveryLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Unnamed Ruin', max_length=255)),
                ('explore_type', models.CharField(default='discovery_location', editable=False, max_length=255)),
                ('direction_degree', models.FloatField(default=0.0)),
                ('direction', models.CharField(default='Unknown', max_length=255)),
                ('miles_away', models.FloatField(default=0.0)),
                ('location_id', models.CharField(default='', max_length=255)),
                ('latitude', models.FloatField(default=0.0)),
                ('longitude', models.FloatField(default=0.0)),
                ('tags', models.JSONField(default=dict)),
                ('wind_compass', models.CharField(default='', max_length=255)),
                ('wind_agreement_score', models.IntegerField(default=0)),
                ('wind_harmony', models.BooleanField(default=False)),
                ('street_view_image', models.URLField(blank=True, default='', null=True)),
                ('created_on', models.DateTimeField()),
                ('last_accessed', models.DateTimeField()),
                ('origin_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='climatevisitor.climatetwinlocation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Archived Discovery Location',
                'verbose_name_plural': 'Archived Discovery Locations',
            },
        ),
    ]
