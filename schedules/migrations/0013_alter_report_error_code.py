# Generated by Django 3.2.6 on 2022-01-31 07:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0012_report_email_sent_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='error_code',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='エラーコード'),
        ),
    ]
