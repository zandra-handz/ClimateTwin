# Generated by Django 5.0.1 on 2024-02-03 00:47

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usersettings',
            options={'verbose_name': 'User settings', 'verbose_name_plural': 'User settings'},
        ),
        migrations.AddField(
            model_name='uservisit',
            name='location_latitude',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='uservisit',
            name='location_longitude',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('NB', 'Non-Binary'), ('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('No answer', 'Uninterested in answering this')], default='', max_length=10, verbose_name='gender'),
        ),
        migrations.AlterField(
            model_name='uservisit',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='Treasure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_user', models.CharField(default='', max_length=50)),
                ('location_name', models.CharField(max_length=255)),
                ('found_at_latitude', models.FloatField(default=0.0)),
                ('found_at_longitude', models.FloatField(default=0.0)),
                ('item_name', models.CharField(default='', max_length=255)),
                ('item_category', models.CharField(default='', max_length=255)),
                ('descriptor', models.CharField(default='', max_length=50)),
                ('description', models.CharField(default='', max_length=600)),
                ('add_data', models.JSONField(default=dict)),
                ('pending', models.BooleanField(default=False)),
                ('message', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('owned_since', models.DateTimeField(blank=True, null=True)),
                ('giver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_gifts', to=settings.AUTH_USER_MODEL)),
                ('recipient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_gifts', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='treasures', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ItemInbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='inbox', to=settings.AUTH_USER_MODEL)),
                ('items', models.ManyToManyField(related_name='user_items', to='users.treasure')),
            ],
            options={
                'verbose_name': 'Inbox',
                'verbose_name_plural': 'Inboxes',
            },
        ),
        migrations.CreateModel(
            name='UserFriendz',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nickname', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('friend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_of', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friends', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='CollectedItem',
        ),
    ]
