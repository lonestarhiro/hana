# Generated by Django 3.2.6 on 2021-11-28 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careusers', '0006_alter_defaultschedule_weektype'),
    ]

    operations = [
        migrations.AddField(
            model_name='defaultschedule',
            name='no_set_staff',
            field=models.BooleanField(default=False, verbose_name='スタッフを自動入力しない'),
        ),
    ]