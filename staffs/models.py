from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sei = models.CharField(verbose_name="姓",max_length=10)
    mei = models.CharField(verbose_name="名",max_length=10)
    kana_sei = models.CharField(verbose_name="せい",max_length=10)
    kana_mei = models.CharField(verbose_name="めい",max_length=10)
    birthday = models.DateField(verbose_name="生年月日")
    staff_no = models.PositiveSmallIntegerField(verbose_name="社員番号",blank=True)
    postcode = models.CharField(verbose_name="郵便番号",max_length=7)
    adr_ken  = models.CharField(verbose_name="県",max_length=4)
    adr_siku = models.CharField(verbose_name="市区町村",max_length=30)
    adr_tyou = models.CharField(verbose_name="町名・番地",max_length=30)
    adr_bld  = models.CharField(verbose_name="ビル・マンション名",max_length=40,default="",blank=True)
    tel      = models.CharField(verbose_name="電話番号",max_length=15,default="",blank=True)
    phone    = models.CharField(verbose_name="携帯",max_length=15,default="",blank=True)
    email    = models.EmailField(verbose_name="メールアドレス", unique=True)
    shaho    = models.BooleanField(verbose_name="社会保険加入",default=False)
    join     = models.DateField(verbose_name="入社日")
    biko     = models.TextField(verbose_name="備考",default="",blank=True)
    kanri    = models.BooleanField(verbose_name="管理者",default=False)
    jimu     = models.BooleanField(verbose_name="事務員",default=False)
    reader   = models.BooleanField(verbose_name="グループリーダー",default=False)
    caremane = models.BooleanField(verbose_name="ケアマネージャー",default=False)
    servkan  = models.BooleanField(verbose_name="サービス提供責任者",default=False)
    kaigo    = models.BooleanField(verbose_name="介護職員",default=False)
    yougu    = models.BooleanField(verbose_name="福祉用具専門相談員",default=False)
    kango    = models.BooleanField(verbose_name="看護職員",default=False)
    kinou    = models.BooleanField(verbose_name="機能訓練指導員",default=False)
    seikatu  = models.BooleanField(verbose_name="生活相談員",default=False)
    ishi     = models.BooleanField(verbose_name="医師",default=False)
    riha     = models.BooleanField(verbose_name="リハ職員",default=False)
    ope      = models.BooleanField(verbose_name="オペレーター",default=False)
    ryouyou  = models.BooleanField(verbose_name="療養管理指導員",default=False)
    jihakan  = models.BooleanField(verbose_name="児童発達支援管理責任者",default=False)
    sidou    = models.BooleanField(verbose_name="指導員",default=False)
    hoiku    = models.BooleanField(verbose_name="保育士",default=False)
    jisou    = models.BooleanField(verbose_name="児童指導員",default=False)
    driver   = models.BooleanField(verbose_name="ドライバー",default=False)
    eiyou    = models.BooleanField(verbose_name="栄養士",default=False)
    tyouri   = models.BooleanField(verbose_name="調理師",default=False)
    gengo    = models.BooleanField(verbose_name="言語機能訓練指導員",default=False)
    tyounou  = models.BooleanField(verbose_name="聴能訓練指導員",default=False)

    def __str__(self):
        return f'{self.user}'