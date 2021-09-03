from django.db import models

kind_choice =[(0,"介護"),(1,"障害"),(2,"移動支援"),(3,"自費"),]

class Service(models.Model):
    kind     = models.PositiveSmallIntegerField(verbose_name="請求種別",default=0,choices=kind_choice)
    title    = models.CharField(verbose_name="名称",max_length=30)
    time     = models.PositiveSmallIntegerField(verbose_name="所要時間(分)")
    #2名３名の場合は？


    def __str__(self):
        return f"{self.get_kind_display()} {self.title}" 