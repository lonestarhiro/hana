from django.db import models

class CareUser(models.Model):

    gender_choice =[(0,"男"),(1,"女"),]
  
    last_name  = models.CharField(verbose_name="姓",max_length=30)
    first_name = models.CharField(verbose_name="名",max_length=30)
    last_kana  = models.CharField(verbose_name="せい",max_length=30)
    first_kana = models.CharField(verbose_name="めい",max_length=30)
    gender     = models.PositiveSmallIntegerField(verbose_name="性別",default=0,choices=gender_choice)
    birthday   = models.DateField(verbose_name="生年月日",blank=True)
    user_no    = models.PositiveSmallIntegerField(verbose_name="利用者番号",blank=True, null=True,unique=True)
    postcode   = models.CharField(verbose_name="郵便番号",max_length=7)
    adr_ken    = models.CharField(verbose_name="都道府県",max_length=4)
    adr_siku   = models.CharField(verbose_name="市区町村",max_length=30)
    adr_tyou   = models.CharField(verbose_name="町名・番地",max_length=30)
    adr_bld    = models.CharField(verbose_name="ビル・マンション名",max_length=40,default="",blank=True)
    tel        = models.CharField(verbose_name="電話番号",max_length=15,default="",blank=True)
    phone      = models.CharField(verbose_name="携帯",max_length=15,default="",blank=True)
    startdate  = models.DateField(verbose_name="契約日",blank=True)
    biko       = models.TextField(verbose_name="備考",default="",blank=True)
    is_active  = models.BooleanField(verbose_name="利用中",default=True)

    def __str__(self):
        return f"{self.last_name} + " " + {self.first_name}" 


class DefaultSchedule(models.Model):

    type_choice = [(0,"曜日指定"),(1,"日指定")]
    weektype_choice = [(0,"毎週"),(1,"隔週1-3-5"),(2,"隔週2-4"),(3,"第1"),(4,"第2"),(5,"第3"),(6,"第4")]
    daytype_choice  = [(0,"毎日"),(1,"奇数日"),(2,"偶数日"),(3,"日付指定")]

    careuser = models.ForeignKey(CareUser,on_delete=models.CASCADE)
    type     = models.PositiveSmallIntegerField(verbose_name="",default=0,choices=type_choice)
    weektype = models.PositiveSmallIntegerField(verbose_name="",default=0,choices=weektype_choice)
    sun      = models.BooleanField(verbose_name="日",default=False)
    mon      = models.BooleanField(verbose_name="月",default=False)
    tue      = models.BooleanField(verbose_name="火",default=False)
    wed      = models.BooleanField(verbose_name="水",default=False)
    thu      = models.BooleanField(verbose_name="木",default=False)
    fri      = models.BooleanField(verbose_name="金",default=False)
    sat      = models.BooleanField(verbose_name="土",default=False)
    daytype  = models.PositiveSmallIntegerField(verbose_name="",default=0,choices=daytype_choice)
    day      = models.PositiveSmallIntegerField(verbose_name="日",blank=True, null=True)
    biko     = models.TextField(verbose_name="備考",default="",blank=True)
    