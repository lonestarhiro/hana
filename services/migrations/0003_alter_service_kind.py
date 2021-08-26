# Generated by Django 3.2.6 on 2021-08-26 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_alter_service_kind'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='kind',
            field=models.PositiveSmallIntegerField(choices=[(0, '介護'), (1, '障害'), (2, '移動支援'), (3, '自費')], default=0, verbose_name='請求種別'),
        ),
    ]
