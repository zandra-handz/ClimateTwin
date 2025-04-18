# Generated by Django 5.0.2 on 2025-04-10 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0033_treasure_finder'),
    ]

    operations = [
        migrations.AddField(
            model_name='badrainbowzuser',
            name='is_subscribed_user',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='badrainbowzuser',
            name='subscription_expiration_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
