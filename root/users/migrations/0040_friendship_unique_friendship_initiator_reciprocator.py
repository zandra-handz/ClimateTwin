# Generated by Django 5.0.2 on 2025-04-20 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0039_friendprofile_users_frien_user_id_082a8e_idx'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='friendship',
            constraint=models.UniqueConstraint(fields=('initiator', 'reciprocator'), name='unique_friendship_initiator_reciprocator'),
        ),
    ]
