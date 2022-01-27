# Generated by Django 3.2.6 on 2022-01-27 16:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0007_auto_20220127_1816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='blood_pre_l',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(300)], verbose_name='血圧Low'),
        ),
        migrations.AlterField(
            model_name='report',
            name='deposit',
            field=models.PositiveIntegerField(blank=True, default=0, validators=[django.core.validators.MaxValueValidator(999999)], verbose_name='預り金'),
        ),
        migrations.AlterField(
            model_name='report',
            name='payment',
            field=models.PositiveIntegerField(blank=True, default=0, validators=[django.core.validators.MaxValueValidator(999999)], verbose_name='買物'),
        ),
    ]
