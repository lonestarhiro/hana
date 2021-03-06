# Generated by Django 3.2.6 on 2022-01-25 22:04

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CareUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=30, verbose_name='姓')),
                ('first_name', models.CharField(max_length=30, verbose_name='名')),
                ('short_name', models.CharField(blank=True, default='', max_length=30, verbose_name='短縮名')),
                ('last_kana', models.CharField(max_length=30, verbose_name='せい')),
                ('first_kana', models.CharField(max_length=30, verbose_name='めい')),
                ('gender', models.PositiveSmallIntegerField(choices=[(0, '男'), (1, '女')], default=0, verbose_name='性別')),
                ('birthday', models.DateField(blank=True, verbose_name='生年月日')),
                ('report_send', models.BooleanField(default=False, verbose_name='サービス実施記録メール送信')),
                ('report_email', models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='サービス実施記録送信先メールアドレス')),
                ('user_no', models.PositiveSmallIntegerField(blank=True, null=True, unique=True, verbose_name='利用者番号')),
                ('postcode', models.CharField(max_length=7, verbose_name='郵便番号')),
                ('adr_ken', models.CharField(max_length=4, verbose_name='都道府県')),
                ('adr_siku', models.CharField(max_length=30, verbose_name='市区町村')),
                ('adr_tyou', models.CharField(max_length=30, verbose_name='町名・番地')),
                ('adr_bld', models.CharField(blank=True, default='', max_length=40, verbose_name='ビル・マンション名')),
                ('tel', models.CharField(blank=True, default='', max_length=15, verbose_name='電話番号')),
                ('phone', models.CharField(blank=True, default='', max_length=15, verbose_name='携帯')),
                ('startdate', models.DateField(blank=True, null=True, verbose_name='契約日')),
                ('biko', models.TextField(blank=True, default='', verbose_name='備考')),
                ('is_active', models.BooleanField(default=True, verbose_name='利用中')),
                ('no_active_date', models.DateField(blank=True, null=True, verbose_name='利用終了日時')),
            ],
        ),
        migrations.CreateModel(
            name='DefaultSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField(choices=[(0, '週ベース'), (1, '日ベース')], default=0, verbose_name='')),
                ('weektype', models.PositiveSmallIntegerField(choices=[(0, '毎週'), (1, '隔週1-3-5'), (2, '隔週2-4'), (3, '第1'), (4, '第2'), (5, '第3'), (6, '第4'), (7, '第5')], default=0, verbose_name='週指定')),
                ('sun', models.BooleanField(default=False, verbose_name='日')),
                ('mon', models.BooleanField(default=False, verbose_name='月')),
                ('tue', models.BooleanField(default=False, verbose_name='火')),
                ('wed', models.BooleanField(default=False, verbose_name='水')),
                ('thu', models.BooleanField(default=False, verbose_name='木')),
                ('fri', models.BooleanField(default=False, verbose_name='金')),
                ('sat', models.BooleanField(default=False, verbose_name='土')),
                ('daytype', models.PositiveSmallIntegerField(choices=[(0, '毎日'), (1, '奇数日'), (2, '偶数日'), (3, '日付指定')], default=0, verbose_name='日指定')),
                ('day', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(31)], verbose_name='日付')),
                ('biko', models.TextField(blank=True, default='', verbose_name='備考')),
                ('start_h', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(23)], verbose_name='開始時')),
                ('start_m', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(59)], verbose_name='開始分')),
                ('peoples', models.PositiveSmallIntegerField(choices=[(1, '1名'), (2, '2名'), (3, '3名'), (4, '4名')], default=1, verbose_name='必要人数')),
                ('no_set_staff', models.BooleanField(default=False, verbose_name='スタッフを自動入力しない')),
                ('careuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='careusers.careuser', verbose_name='利用者名')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='services.service', verbose_name='利用サービス')),
            ],
        ),
    ]
