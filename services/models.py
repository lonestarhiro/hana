from django.db import models

kind_choice =[(0,"介護保険"),(1,"障害者総合支援"),(2,"移動支援"),(3,"総合事業"),(4,"同行援護"),( 5,"自費"),( 9,"その他")]

class Service(models.Model):
    kind          = models.PositiveSmallIntegerField(verbose_name="請求種別",default=0,choices=kind_choice)
    bill_title    = models.CharField(verbose_name="請求名称",max_length=50,default="")
    user_title    = models.CharField(verbose_name="利用者様用名称",max_length=50,default="")
    title         = models.CharField(verbose_name="システム名称",max_length=50)
    time          = models.PositiveSmallIntegerField(verbose_name="標準総所要時間(分)")
    min_time      = models.PositiveSmallIntegerField(verbose_name="最低時間(単一サービス時)",default=0,blank=True)
    mix_items     = models.BooleanField(verbose_name="複数サービス混合",default=False)
    name_main     = models.CharField(verbose_name="名称メイン",max_length=50,default="",blank=True)
    in_time_main  = models.PositiveSmallIntegerField(verbose_name="標準内訳時間メイン(分)",default=0,blank=True)
    min_time_main = models.PositiveSmallIntegerField(verbose_name="最低時間メイン(分)",default=0)
    name_sub      = models.CharField(verbose_name="名称サブ",max_length=50,default="",blank=True)
    in_time_sub   = models.PositiveSmallIntegerField(verbose_name="標準内訳時間サブ(分)",default=0,blank=True)
    min_time_sub  = models.PositiveSmallIntegerField(verbose_name="最低時間サブ(分)",default=0,blank=True)
    destination   = models.BooleanField(verbose_name="行先入力必須",default=False)
    is_active     = models.BooleanField(verbose_name="使用中",default=True)
    biko          = models.TextField(verbose_name="備考",default="",blank=True)

    def __str__(self):
        return f"{self.get_kind_display()} {self.title}" 