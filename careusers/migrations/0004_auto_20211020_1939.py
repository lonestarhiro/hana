# Generated by Django 3.2.6 on 2021-10-20 10:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careusers', '0003_auto_20211020_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultschedule',
            name='day',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.RegexValidator(message='日付の入力を確認してください。', regex='0[1-9]|[12][0-9]|3[01]')], verbose_name='日付'),
        ),
        migrations.AlterField(
            model_name='defaultschedule',
            name='start_h',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.RegexValidator(message='時の入力を確認してください。', regex='[01][0-9]|2[0-3]')], verbose_name='開始時'),
        ),
        migrations.AlterField(
            model_name='defaultschedule',
            name='start_m',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.RegexValidator(message='分の入力を確認してください。', regex='[0-5][0-9]')], verbose_name='開始分'),
        ),
    ]