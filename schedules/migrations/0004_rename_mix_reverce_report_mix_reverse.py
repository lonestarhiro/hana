# Generated by Django 3.2.6 on 2022-01-26 03:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0003_auto_20220126_0708'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='mix_reverce',
            new_name='mix_reverse',
        ),
    ]