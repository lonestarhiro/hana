# Generated by Django 3.2.6 on 2022-02-07 15:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0017_alter_report_error_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='eating',
            field=models.PositiveSmallIntegerField(choices=[(0, '---'), (1, '全'), (2, '一部')], default=0, validators=[django.core.validators.MaxValueValidator(2)], verbose_name='摂食介助'),
        ),
    ]
