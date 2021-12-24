# Generated by Django 3.2.6 on 2021-12-23 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0005_alter_report_locked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='comfirm_flg',
        ),
        migrations.AddField(
            model_name='schedule',
            name='cancel_flg',
            field=models.BooleanField(default=False, verbose_name='予定キャンセル'),
        ),
    ]