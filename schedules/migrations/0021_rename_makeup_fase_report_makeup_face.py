# Generated by Django 3.2.6 on 2021-09-21 03:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0020_auto_20210921_0907'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='makeup_fase',
            new_name='makeup_face',
        ),
    ]
