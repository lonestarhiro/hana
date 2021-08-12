# Generated by Django 3.2.6 on 2021-08-12 08:58

from django.db import migrations, models
import django.utils.timezone
import staffs.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='メールアドレス')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='名')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='姓')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_kana', models.CharField(max_length=30, verbose_name='めい')),
                ('last_kana', models.CharField(max_length=30, verbose_name='せい')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='生年月日')),
                ('staff_no', models.PositiveSmallIntegerField(blank=True, null=True, unique=True, verbose_name='社員番号')),
                ('postcode', models.CharField(max_length=7, verbose_name='郵便番号')),
                ('adr_ken', models.CharField(max_length=4, verbose_name='県')),
                ('adr_siku', models.CharField(max_length=30, verbose_name='市区町村')),
                ('adr_tyou', models.CharField(max_length=30, verbose_name='町名・番地')),
                ('adr_bld', models.CharField(blank=True, default='', max_length=40, verbose_name='ビル・マンション名')),
                ('tel', models.CharField(blank=True, default='', max_length=15, verbose_name='電話番号')),
                ('phone', models.CharField(blank=True, default='', max_length=15, verbose_name='携帯')),
                ('shaho', models.BooleanField(default=False, verbose_name='社会保険加入')),
                ('join', models.DateField(blank=True, null=True, verbose_name='入社日')),
                ('biko', models.TextField(blank=True, default='', verbose_name='備考')),
                ('kanri', models.BooleanField(default=False, verbose_name='管理者')),
                ('jimu', models.BooleanField(default=False, verbose_name='事務員')),
                ('reader', models.BooleanField(default=False, verbose_name='グループリーダー')),
                ('caremane', models.BooleanField(default=False, verbose_name='ケアマネージャー')),
                ('servkan', models.BooleanField(default=False, verbose_name='サービス提供責任者')),
                ('kaigo', models.BooleanField(default=False, verbose_name='介護職員')),
                ('yougu', models.BooleanField(default=False, verbose_name='福祉用具専門相談員')),
                ('kango', models.BooleanField(default=False, verbose_name='看護職員')),
                ('kinou', models.BooleanField(default=False, verbose_name='機能訓練指導員')),
                ('seikatu', models.BooleanField(default=False, verbose_name='生活相談員')),
                ('ishi', models.BooleanField(default=False, verbose_name='医師')),
                ('riha', models.BooleanField(default=False, verbose_name='リハ職員')),
                ('ope', models.BooleanField(default=False, verbose_name='オペレーター')),
                ('ryouyou', models.BooleanField(default=False, verbose_name='療養管理指導員')),
                ('jihakan', models.BooleanField(default=False, verbose_name='児童発達支援管理責任者')),
                ('sidou', models.BooleanField(default=False, verbose_name='指導員')),
                ('hoiku', models.BooleanField(default=False, verbose_name='保育士')),
                ('jisou', models.BooleanField(default=False, verbose_name='児童指導員')),
                ('driver', models.BooleanField(default=False, verbose_name='ドライバー')),
                ('eiyou', models.BooleanField(default=False, verbose_name='栄養士')),
                ('tyouri', models.BooleanField(default=False, verbose_name='調理師')),
                ('gengo', models.BooleanField(default=False, verbose_name='言語機能訓練指導員')),
                ('tyounou', models.BooleanField(default=False, verbose_name='聴能訓練指導員')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', staffs.models.CustomUserManager()),
            ],
        ),
    ]
