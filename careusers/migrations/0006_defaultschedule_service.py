# Generated by Django 3.2.6 on 2021-08-19 06:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_alter_service_kind'),
        ('careusers', '0005_auto_20210819_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='defaultschedule',
            name='service',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.RESTRICT, to='services.service', verbose_name='利用サービス'),
            preserve_default=False,
        ),
    ]
