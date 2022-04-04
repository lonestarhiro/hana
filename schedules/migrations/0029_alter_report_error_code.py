# Generated by Django 3.2.6 on 2022-04-04 15:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0028_alter_report_error_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='error_code',
            field=models.PositiveSmallIntegerField(choices=[(0, 'なし'), (11, '開始・終了時間不整合'), (12, '実績合計時間が内訳合計時間と不一致'), (13, 'サービス実施時間が最低時間以下'), (14, 'サービス実施時間が15分以上超過'), (15, '年月が不一致'), (16, '担当スタッフの移動時間が5分未満'), (17, 'サービス必要人員数不足'), (90, '開始時間・終了時間が未入力')], default=0, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='エラーコード'),
        ),
    ]
