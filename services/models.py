from django.db import models

kind_choice =[(0,"介護保険"),(1,"障害者総合支援"),(2,"移動支援"),(3,"自費"),]

class Service(models.Model):
    kind       = models.PositiveSmallIntegerField(verbose_name="請求種別",default=0,choices=kind_choice)
    title      = models.CharField(verbose_name="名称",max_length=50)
    time       = models.PositiveSmallIntegerField(verbose_name="所要時間(分)")
    points     = models.PositiveSmallIntegerField(verbose_name="点数",default=0,blank=True)
    is_active  = models.BooleanField(verbose_name="使用中",default=True)
    biko       = models.TextField(verbose_name="備考",default="",blank=True)
    #2名３名の場合は？


    def __str__(self):
        return f"{self.get_kind_display()} {self.title}" 