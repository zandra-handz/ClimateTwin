# Generated by Django 5.0.1 on 2024-02-05 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_treasure_miles_traveled_to_collect'),
    ]

    operations = [
        migrations.AlterField(
            model_name='treasure',
            name='descriptor',
            field=models.CharField(default='Mystery Item', max_length=50),
        ),
        migrations.AlterField(
            model_name='uservisit',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]