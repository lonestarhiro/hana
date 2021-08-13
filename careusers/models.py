from django.db import models

class Careuser(models.Model):

    gender_choise ={(0,"男"),(1,"女")}
  
    last_name  = models.CharField(verbose_name="姓",max_length=30)
    first_name = models.CharField(verbose_name="名",max_length=30)
    last_kana  = models.CharField(verbose_name="せい",max_length=30)
    first_kana = models.CharField(verbose_name="めい",max_length=30)
    gender     = models.PositiveSmallIntegerField(verbose_name="性別",max_length=1,choices=gender_choise),
    birthday   = models.DateField(verbose_name="生年月日",blank=True)
    user_no    = models.PositiveSmallIntegerField(verbose_name="利用者番号",blank=True, null=True,unique=True)
    postcode   = models.CharField(verbose_name="郵便番号",max_length=7)
    adr_ken    = models.CharField(verbose_name="県",max_length=4)
    adr_siku   = models.CharField(verbose_name="市区町村",max_length=30)
    adr_tyou   = models.CharField(verbose_name="町名・番地",max_length=30)
    adr_bld    = models.CharField(verbose_name="ビル・マンション名",max_length=40,default="",blank=True)
    tel        = models.CharField(verbose_name="電話番号",max_length=15,default="",blank=True)
    phone      = models.CharField(verbose_name="携帯",max_length=15,default="",blank=True)
    startdate  = models.DateField(verbose_name="契約日",blank=True)
    biko       = models.TextField(verbose_name="備考",default="",blank=True)
    is_active  = models.BooleanField(verbose_name="利用中",default=True)