# Generated by Django 5.0.1 on 2024-02-03 02:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_usersettings_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='iteminbox',
            name='items',
        ),
        migrations.DeleteModel(
            name='Treasure',
        ),
    ]