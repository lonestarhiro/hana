# Generated by Django 3.2.6 on 2021-09-10 10:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0014_auto_20210910_1508'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('face_color', models.PositiveSmallIntegerField(choices=[(0, '---'), (1, '良'), (2, '不良')], default=0, verbose_name='顔色')),
                ('hakkan', models.PositiveSmallIntegerField(choices=[(0, '---'), (1, '良'), (2, '不良')], default=0, verbose_name='発汗')),
                ('body_temp', models.FloatField(blank=True, null=True, verbose_name='体温')),
                ('blood_pre_h', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='血圧High')),
                ('blood_pre_l', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='血圧Low')),
                ('after_fire', models.BooleanField(default=False, verbose_name='火元')),
                ('after_elec', models.BooleanField(default=False, verbose_name='電気')),
                ('after_water', models.BooleanField(default=False, verbose_name='水道')),
                ('after_close', models.BooleanField(default=False, verbose_name='戸締り')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedules.schedule', verbose_name='スケジュール')),
            ],
        ),
    ]
