# Generated by Django 3.2.6 on 2021-09-05 21:44

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('careusers', '__first__'),
        ('schedules', '0004_auto_20210903_1614'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='def_sche_id',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='service',
        ),
        migrations.AddField(
            model_name='schedule',
            name='def_sche',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='def_sche', to='careusers.defaultschedule', verbose_name='標準スケジュールからの登録'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='idou_point',
            field=models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='移動支援点数'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='jihi_point',
            field=models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='自費点数換算'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='service_titile',
            field=models.CharField(default=django.utils.timezone.now, max_length=50, verbose_name='利用サービス'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='schedule',
            name='staff_check_level',
            field=models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='スタッフチェックフラグ'),
        ),
    ]
