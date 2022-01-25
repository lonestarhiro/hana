# Generated by Django 3.2.6 on 2022-01-25 22:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('services', '0001_initial'),
        ('careusers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedules', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='showuserenddate',
            name='updated_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL, verbose_name='更新者'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='careuser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='careusers.careuser', verbose_name='利用者名'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL, verbose_name='登録スタッフ'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='def_sche',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='def_sche', to='careusers.defaultschedule', verbose_name='標準スケジュールからの登録'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='service',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='services.service', verbose_name='利用サービス'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='staff1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='staffs1', to=settings.AUTH_USER_MODEL, verbose_name='担当スタッフ１'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='staff2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='staffs2', to=settings.AUTH_USER_MODEL, verbose_name='担当スタッフ２'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='staff3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='staffs3', to=settings.AUTH_USER_MODEL, verbose_name='担当スタッフ３'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='staff4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='staffs4', to=settings.AUTH_USER_MODEL, verbose_name='担当スタッフ４'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='tr_staff1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='tr_staffs1', to=settings.AUTH_USER_MODEL, verbose_name='研修スタッフ１'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='tr_staff2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='tr_staffs2', to=settings.AUTH_USER_MODEL, verbose_name='研修スタッフ２'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='tr_staff3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='tr_staffs3', to=settings.AUTH_USER_MODEL, verbose_name='研修スタッフ３'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='tr_staff4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='tr_staffs4', to=settings.AUTH_USER_MODEL, verbose_name='研修スタッフ４'),
        ),
        migrations.AddField(
            model_name='report',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL, verbose_name='登録スタッフ'),
        ),
        migrations.AddField(
            model_name='report',
            name='schedule',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='schedules.schedule'),
        ),
    ]
