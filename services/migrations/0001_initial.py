# Generated by Django 3.2.6 on 2021-09-23 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.PositiveSmallIntegerField(choices=[(0, '介護保険'), (1, '障害者総合支援'), (2, '移動支援'), (3, '自費')], default=0, verbose_name='請求種別')),
                ('title', models.CharField(max_length=50, verbose_name='名称')),
                ('time', models.PositiveSmallIntegerField(verbose_name='所要時間(分)')),
                ('points', models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='点数')),
                ('is_active', models.BooleanField(default=True, verbose_name='使用中')),
                ('biko', models.TextField(blank=True, default='', verbose_name='備考')),
            ],
        ),
    ]