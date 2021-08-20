from django.db import models
from services.models import Service
from staffs.models import User
from careusers.models import CareUser
import datetime
from django.utils.timezone import localtime

class Schedule(models.Model):

    careuser     = models.ForeignKey(CareUser,verbose_name="利用者名",on_delete=models.RESTRICT)
    date         = models.DateTimeField(verbose_name="日時")
    service      = models.ForeignKey(Service,verbose_name="利用サービス",on_delete=models.RESTRICT)
    staff1       = models.ForeignKey(User,verbose_name="担当スタッフ１",blank=True,null=True,related_name = "staffs1",on_delete=models.RESTRICT)
    staff2       = models.ForeignKey(User,verbose_name="担当スタッフ２",blank=True,null=True,related_name = "staffs2",on_delete=models.RESTRICT)
    staff3       = models.ForeignKey(User,verbose_name="担当スタッフ３",blank=True,null=True,related_name = "staffs3",on_delete=models.RESTRICT)
    staff4       = models.ForeignKey(User,verbose_name="担当スタッフ４",blank=True,null=True,related_name = "staffs4",on_delete=models.RESTRICT)
    tr_staff1    = models.ForeignKey(User,verbose_name="研修スタッフ１",blank=True,null=True,related_name = "tr_staffs1",on_delete=models.RESTRICT)
    tr_staff2    = models.ForeignKey(User,verbose_name="研修スタッフ２",blank=True,null=True,related_name = "tr_staffs2",on_delete=models.RESTRICT)
    tr_staff3    = models.ForeignKey(User,verbose_name="研修スタッフ３",blank=True,null=True,related_name = "tr_staffs3",on_delete=models.RESTRICT)
    tr_staff4    = models.ForeignKey(User,verbose_name="研修スタッフ４",blank=True,null=True,related_name = "tr_staffs4",on_delete=models.RESTRICT)
    biko         = models.TextField(verbose_name="備考",default="",blank=True)
    kaigo_point  = models.PositiveSmallIntegerField(verbose_name="介護点数",default=0,blank=True)
    shogai_point = models.PositiveSmallIntegerField(verbose_name="障害点数",default=0,blank=True)
    from_default = models.BooleanField(verbose_name="DefaultScheduleからの登録",default=False)


    def __str__(self):
        return f"{self.careuser}" 

    ##終了時刻はサービステーブルを作成後、サービス時間より計算して表示させる
    def get_end_time(self):
        endtime = self.date + datetime.timedelta(minutes = self.service.time)
        endtime = localtime(endtime)
        return endtime

    def staffs(self):
        name_staffs  = ""
        #スタッフ表示
        if self.staff1 != None:
            name_staffs += self.staff1.get_short_name()
        if self.staff2 != None:
            if name_staffs  != "":
               name_staffs += "・" 
            name_staffs += self.staff2.get_short_name()
        if self.staff3 != None:
            if name_staffs  != "":
                   name_staffs += "・" 
            name_staffs += self.staff3.get_short_name()
        if self.staff4 != None:
            if name_staffs  != "":
                   name_staffs += "・" 
            name_staffs += self.staff4.get_short_name()

        return name_staffs
