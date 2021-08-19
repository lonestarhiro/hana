# Generated by Django 3.2.6 on 2021-08-19 05:44

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
                ('kind', models.PositiveSmallIntegerField(choices=[(0, '介護保険'), (1, '障害'), (2, '自費')], default=0, verbose_name='請求種別')),
                ('title', models.CharField(max_length=30, verbose_name='名称')),
                ('time', models.PositiveSmallIntegerField(verbose_name='所要時間(分)')),
            ],
        ),
    ]
