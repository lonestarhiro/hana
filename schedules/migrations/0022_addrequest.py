# Generated by Django 3.2.6 on 2022-02-13 11:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedules', '0021_alter_schedule_updated_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(verbose_name='日時')),
                ('careuser_txt', models.CharField(max_length=20, verbose_name='利用者名')),
                ('service_txt', models.CharField(max_length=30, verbose_name='サービス内容')),
                ('biko', models.TextField(blank=True, default='', max_length=200, verbose_name='特記・連絡事項')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日')),
                ('confirmed_at', models.DateTimeField(blank=True, null=True, verbose_name='確認日')),
                ('confirmed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='confirmed_by', to=settings.AUTH_USER_MODEL, verbose_name='確認スタッフ')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL, verbose_name='登録スタッフ')),
            ],
        ),
    ]
