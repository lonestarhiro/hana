# Generated by Django 3.2.6 on 2021-10-27 16:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careusers', '0004_auto_20211020_1939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultschedule',
            name='day',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(31)], verbose_name='日付'),
        ),
        migrations.AlterField(
            model_name='defaultschedule',
            name='start_h',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(23)], verbose_name='開始時'),
        ),
        migrations.AlterField(
            model_name='defaultschedule',
            name='start_m',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(59)], verbose_name='開始分'),
        ),
    ]