# Generated by Django 3.2.6 on 2022-01-31 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careusers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='defaultschedule',
            name='add_stop',
            field=models.BooleanField(default=False, verbose_name='予定を自動追加しない'),
        ),
    ]
