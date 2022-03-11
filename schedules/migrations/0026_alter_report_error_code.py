# Generated by Django 3.2.6 on 2022-03-11 12:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0025_alter_report_urination_a'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='error_code',
            field=models.PositiveSmallIntegerField(choices=[(0, 'なし'), (11, '開始・終了時間不整合'), (12, '実績合計時間が内訳合計時間と不一致'), (13, 'サービス実施時間が最低時間以下'), (14, 'サービス実施時間が15分以上超過'), (15, '日付が不一致'), (90, '開始時間・終了時間が未入力')], default=0, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='エラーコード'),
        ),
    ]
