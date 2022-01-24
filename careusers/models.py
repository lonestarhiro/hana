from services.models import Service
from django.db import models
from staffs.models import User
import datetime
from django.utils import timezone
from django.core.validators import RegexValidator,MinValueValidator,MaxValueValidator

class CareUser(models.Model):

    gender_choice =[(0,"男"),(1,"女"),]
  
    last_name      = models.CharField(verbose_name="姓",max_length=30)
    first_name     = models.CharField(verbose_name="名",max_length=30)
    short_name     = models.CharField(verbose_name="短縮名",max_length=30,default="",blank=True)
    last_kana      = models.CharField(verbose_name="せい",max_length=30)
    first_kana     = models.CharField(verbose_name="めい",max_length=30)
    gender         = models.PositiveSmallIntegerField(verbose_name="性別",default=0,choices=gender_choice)
    birthday       = models.DateField(verbose_name="生年月日",blank=True)
    report_send    = models.BooleanField(verbose_name="サービス実施記録メール送信",default=False)
    report_email   = models.EmailField(verbose_name="サービス実施記録送信先メールアドレス",blank=True,null=True,unique=True)
    user_no        = models.PositiveSmallIntegerField(verbose_name="利用者番号",blank=True, null=True,unique=True)
    postcode       = models.CharField(verbose_name="郵便番号",max_length=7)
    adr_ken        = models.CharField(verbose_name="都道府県",max_length=4)
    adr_siku       = models.CharField(verbose_name="市区町村",max_length=30)
    adr_tyou       = models.CharField(verbose_name="町名・番地",max_length=30)
    adr_bld        = models.CharField(verbose_name="ビル・マンション名",max_length=40,default="",blank=True)
    tel            = models.CharField(verbose_name="電話番号",max_length=15,default="",blank=True)
    phone          = models.CharField(verbose_name="携帯",max_length=15,default="",blank=True)
    startdate      = models.DateField(verbose_name="契約日",blank=True,null=True)
    biko           = models.TextField(verbose_name="備考",default="",blank=True)
    is_active      = models.BooleanField(verbose_name="利用中",default=True)
    no_active_date = models.DateField(verbose_name="利用終了日時",blank=True,null=True)

    def __str__(self):
        return f"{self.last_name}　{self.first_name}"
    
    def get_short_name(self):
        if self.short_name == None or self.short_name=="":
            s_name = self.last_name
        else:
            s_name = self.short_name
        return s_name
    
    def is_birthday(self):
        #誕生日判定
        birthday_flg = False
        now = datetime.datetime.now()
        now = timezone.make_aware(now)
        if self.birthday:
            if self.birthday.month == now.month and self.birthday.day == now.day:
                birthday_flg=True
        return birthday_flg



class DefaultSchedule(models.Model):

    type_choice = [(0,"週ベース"),(1,"日ベース")]
    weektype_choice = [(0,"毎週"),(1,"隔週1-3-5"),(2,"隔週2-4"),(3,"第1"),(4,"第2"),(5,"第3"),(6,"第4"),(7,"第5")]
    daytype_choice  = [(0,"毎日"),(1,"奇数日"),(2,"偶数日"),(3,"日付指定")]
    peoples_choice = [(1,"1名"),(2,"2名"),(3,"3名"),(4,"4名")]

    day_regex  = [MinValueValidator(0), MaxValueValidator(31)]
    hour_regex = [MinValueValidator(0), MaxValueValidator(23)]
    min_regex  = [MinValueValidator(0), MaxValueValidator(59)]

    careuser = models.ForeignKey(CareUser,verbose_name="利用者名",on_delete=models.CASCADE)
    type     = models.PositiveSmallIntegerField(verbose_name="",default=0,choices=type_choice)
    weektype = models.PositiveSmallIntegerField(verbose_name="週指定",default=0,choices=weektype_choice)
    sun      = models.BooleanField(verbose_name="日",default=False)
    mon      = models.BooleanField(verbose_name="月",default=False)
    tue      = models.BooleanField(verbose_name="火",default=False)
    wed      = models.BooleanField(verbose_name="水",default=False)
    thu      = models.BooleanField(verbose_name="木",default=False)
    fri      = models.BooleanField(verbose_name="金",default=False)
    sat      = models.BooleanField(verbose_name="土",default=False)
    daytype  = models.PositiveSmallIntegerField(verbose_name="日指定",default=0,choices=daytype_choice)
    day      = models.PositiveSmallIntegerField(verbose_name="日付",validators=day_regex,blank=True, null=True)
    biko     = models.TextField(verbose_name="備考",default="",blank=True)
    
    start_h  = models.PositiveSmallIntegerField(verbose_name="開始時",validators=hour_regex,blank=True, null=True)
    start_m  = models.PositiveSmallIntegerField(verbose_name="開始分",validators=min_regex,blank=True, null=True)
    service  = models.ForeignKey(Service,verbose_name="利用サービス",on_delete=models.RESTRICT)
    peoples  = models.PositiveSmallIntegerField(verbose_name="必要人数",default=1,choices=peoples_choice)
    no_set_staff   = models.BooleanField(verbose_name="スタッフを自動入力しない",default=False)
    ##終了時刻はサービステーブルを作成後、サービス時間より計算して表示させる

    def __str__(self):
        return f"{self.careuser}" 

    def get_schedule_name(self):
        name_type  = ""
        name_param = ""
        #サイクル表示
        if self.type == 0:
            name_type = self.get_weektype_display()
            if self.sun == True:
                name_param += " 日"
            if self.mon == True:
                name_param += " 月"
            if self.tue == True:
                name_param += " 火"
            if self.wed == True:
                name_param += " 水"
            if self.thu == True:
                name_param += " 木"
            if self.fri == True:
                name_param += " 金"
            if self.sat == True:
                name_param += " 土"
        elif self.type == 1:
            if self.daytype != 3:
                name_type = self.get_daytype_display()
            else:
                name_type  = "毎月"
                name_param = str(self.day) + "日"

        sche_name = name_type + " " + name_param + " "

        return sche_name

    def get_start_time(self):
        name_time  = ""
        #時間表示
        if self.start_h != "" and self.start_h != None and self.start_m != "" and self.start_m != None :
            name_time  = str(self.start_h).zfill(2) + ":" + str(self.start_m).zfill(2) + " ~ "
        else:
            name_time = ""
            
        return name_time

    def get_end_time(self):
        endtime = ""
        if self.get_start_time() != "":
            start   = datetime.time(self.start_h,self.start_m)
            endtime = datetime.datetime.combine(datetime.date.today(), start) + datetime.timedelta(minutes = self.service.time)
            endtime = endtime.strftime("%H:%M")
        
        return f"{endtime}"
    
