# Generated by Django 3.2.6 on 2021-09-21 00:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0018_auto_20210921_0901'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='report',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='report',
            name='updated_at',
        ),
    ]
