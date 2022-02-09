# Generated by Django 3.2.6 on 2022-02-06 08:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0016_alter_report_error_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='error_code',
            field=models.PositiveSmallIntegerField(choices=[(0, 'なし'), (11, '開始・終了時間不整合'), (12, '実績合計時間が内訳合計時間と不一致'), (13, 'サービス実施時間が最低時間以下'), (14, 'サービス実施時間が15分以上超過'), (15, '2時間以内に他サービス有り'), (16, 'スタッフ必要人数不足'), (17, '同一時間のスタッフ重複'), (41, '実績合計時間が予定時間と不一致'), (42, '内訳時間が予定と不一致'), (43, '開始時間が31分以上乖離'), (44, '利用者スケジュール同一時間重複'), (90, '開始時間・終了時間が未入力')], default=0, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='エラーコード'),
        ),
    ]