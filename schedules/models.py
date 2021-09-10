from django.conf import settings
from django.db import models
from services.models import Service
from staffs.models import User
from careusers.models import CareUser,DefaultSchedule

class Schedule(models.Model):

    peoples_choice = [(1,"1名"),(2,"2名"),(3,"3名"),(4,"4名")]

    careuser       = models.ForeignKey(CareUser,verbose_name="利用者名",on_delete=models.RESTRICT)
    start_date     = models.DateTimeField(verbose_name="予定日時")
    end_date       = models.DateTimeField(verbose_name="予定終了日時",blank=True,null=True)
    service_indate = models.DateTimeField(verbose_name="予定終了日時",blank=True,null=True)
    service_outdate= models.DateTimeField(verbose_name="予定終了日時",blank=True,null=True)
    service        = models.ForeignKey(Service,verbose_name="利用サービス",on_delete=models.RESTRICT,null=True)
    peoples        = models.PositiveSmallIntegerField(verbose_name="必要人数",default=1,choices=peoples_choice)
    staff1         = models.ForeignKey(User,verbose_name="担当スタッフ１",blank=True,null=True,related_name = "staffs1",on_delete=models.RESTRICT)
    staff2         = models.ForeignKey(User,verbose_name="担当スタッフ２",blank=True,null=True,related_name = "staffs2",on_delete=models.RESTRICT)
    staff3         = models.ForeignKey(User,verbose_name="担当スタッフ３",blank=True,null=True,related_name = "staffs3",on_delete=models.RESTRICT)
    staff4         = models.ForeignKey(User,verbose_name="担当スタッフ４",blank=True,null=True,related_name = "staffs4",on_delete=models.RESTRICT)
    tr_staff1      = models.ForeignKey(User,verbose_name="研修スタッフ１",blank=True,null=True,related_name = "tr_staffs1",on_delete=models.RESTRICT)
    tr_staff2      = models.ForeignKey(User,verbose_name="研修スタッフ２",blank=True,null=True,related_name = "tr_staffs2",on_delete=models.RESTRICT)
    tr_staff3      = models.ForeignKey(User,verbose_name="研修スタッフ３",blank=True,null=True,related_name = "tr_staffs3",on_delete=models.RESTRICT)
    tr_staff4      = models.ForeignKey(User,verbose_name="研修スタッフ４",blank=True,null=True,related_name = "tr_staffs4",on_delete=models.RESTRICT)
    biko           = models.TextField(verbose_name="備考",default="",blank=True)
    def_sche       = models.ForeignKey(DefaultSchedule,verbose_name="標準スケジュールからの登録",blank=True,null=True,related_name = "def_sche",on_delete=models.SET_NULL)
    careuser_check_level = models.PositiveSmallIntegerField(verbose_name="利用者チェックフラグ",default=0,blank=True)
    staff_check_level    = models.PositiveSmallIntegerField(verbose_name="スタッフチェックフラグ",default=0,blank=True)
    comfirm_flg    = models.BooleanField(verbose_name="確定済みサイン",default=False)
    created_by     = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name="登録スタッフ",on_delete=models.RESTRICT)
    created_at     = models.DateTimeField(verbose_name="登録日",auto_now_add=True)
    updated_at     = models.DateTimeField(verbose_name="更新日",auto_now=True)


    def __str__(self):
        return f"{self.careuser}" 

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
