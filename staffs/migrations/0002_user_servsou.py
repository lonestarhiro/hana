# Generated by Django 3.2.6 on 2021-09-17 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='servsou',
            field=models.BooleanField(default=False, verbose_name='サービス相談員'),
        ),
    ]
