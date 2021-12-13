from django.conf import settings
from django.db import models
from services.models import Service
from staffs.models import User
from careusers.models import CareUser,DefaultSchedule
import datetime
from django.utils.timezone import make_aware
from django.core.exceptions import ValidationError

#バリデーション
def check_time(datetime_value):
        #現在時刻
        now  = datetime.datetime.now()
        now  = make_aware(now)

        if datetime_value > now:
            raise ValidationError('サービス開始時刻になっていません。')



class Schedule(models.Model):

    peoples_choice = [(1,"1名"),(2,"2名"),(3,"3名"),(4,"4名")]

    careuser       = models.ForeignKey(CareUser,verbose_name="利用者名",on_delete=models.RESTRICT)
    start_date     = models.DateTimeField(verbose_name="予定日時")
    end_date       = models.DateTimeField(verbose_name="予定終了日時",blank=True,null=True)
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

    def staffs_and_trainer(self):
        name_staffs  = ""
        #スタッフと研修員表示
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
        if self.tr_staff1 != None:
            if name_staffs  != "":
                   name_staffs += "・" 
            name_staffs += self.tr_staff1.get_short_name()
        if self.tr_staff2 != None:
            if name_staffs  != "":
               name_staffs += "・" 
            name_staffs += self.tr_staff2.get_short_name()
        if self.tr_staff3 != None:
            if name_staffs  != "":
                   name_staffs += "・" 
            name_staffs += self.tr_staff3.get_short_name()
        if self.tr_staff4 != None:
            if name_staffs  != "":
                   name_staffs += "・" 
            name_staffs += self.tr_staff4.get_short_name()

        return name_staffs

class Report(models.Model):

    schedule    = models.OneToOneField(Schedule,on_delete=models.CASCADE)
    #初回に入力ボタンを押した場合（利用者によってメール送信した場合もあり）にロックする。
    locked      = models.BooleanField(verbose_name="入力ロック（入力後は登録ヘルパーさんは改変不可とします。）",default=False)
    service_in_date = models.DateTimeField(verbose_name="サービス開始日時",validators=[check_time],null=True)
    service_out_date= models.DateTimeField(verbose_name="サービス終了日時",null=True)
    first       = models.BooleanField(verbose_name="初回",default=False)
    emergency   = models.BooleanField(verbose_name="緊急",default=False)
    #事前チェック
    facecolor_choice = [(0,"---"),(1,"良"),(2,"不良")]
    hakkan_choice = [(0,"---"),(1,"有"),(2,"無")]
    face_color   = models.PositiveSmallIntegerField(verbose_name="顔色",default=0,choices=facecolor_choice)
    hakkan       = models.PositiveSmallIntegerField(verbose_name="発汗",default=0,choices=hakkan_choice)
    body_temp    = models.FloatField(verbose_name="体温",blank=True,null=True)
    blood_pre_h  = models.PositiveSmallIntegerField(verbose_name="血圧High",null=True,blank=True)
    blood_pre_l  = models.PositiveSmallIntegerField(verbose_name="血圧Low",null=True,blank=True)
    #退室時
    after_fire   = models.BooleanField(verbose_name="火元",default=False)
    after_elec   = models.BooleanField(verbose_name="電気",default=False)
    after_water  = models.BooleanField(verbose_name="水道",default=False)
    after_close  = models.BooleanField(verbose_name="戸締り",default=False)

    #身体介護/////////////////////////////////////////////////////////////////////////////////////////////////////////
    #排泄介助
    toilet       = models.BooleanField(verbose_name="トイレ介助",default=False)
    p_toilet     = models.BooleanField(verbose_name="Pトイレ介助",default=False)
    Diapers      = models.BooleanField(verbose_name="おむつ交換",default=False)
    Pads         = models.BooleanField(verbose_name="パッド交換",default=False)
    linen        = models.BooleanField(verbose_name="リネン等処理",default=False)
    inbu         = models.BooleanField(verbose_name="陰部清潔",default=False)
    nyouki       = models.BooleanField(verbose_name="尿器洗浄",default=False)
    urination_t  = models.PositiveSmallIntegerField(verbose_name="排尿回数",default=None,null=True,blank=True)
    urination_a  = models.PositiveSmallIntegerField(verbose_name="排尿量",default=None,null=True,blank=True)
    defecation_t = models.PositiveSmallIntegerField(verbose_name="排便回数",default=None,null=True,blank=True)
    defecation_s = models.CharField(verbose_name="排便状態",max_length=50,default="",blank=True)
    #食事介助
    eating_choice = [(0,"---"),(1,"完食"),(2,"一部")]
    posture      = models.BooleanField(verbose_name="姿勢の確保",default=False)
    eating       = models.PositiveSmallIntegerField(verbose_name="摂食介助",default=0,choices=eating_choice)
    eat_a        = models.CharField(verbose_name="食事量",max_length=3,default="",blank=True)
    drink_a      = models.CharField(verbose_name="水分補給",max_length=4,default="",blank=True)
    #清拭入浴
    bedbath_choice = [(0,"---"),(1,"全身"),(2,"部分")]
    bath_choice  = [(0,"---"),(1,"全身浴"),(2,"全身シャワー浴"),(3,"部分浴：手"),(4,"部分浴：足"),(5,"部分浴：手足")]
    bedbath      = models.PositiveSmallIntegerField(verbose_name="清拭",default=0,choices=bedbath_choice)
    bath         = models.PositiveSmallIntegerField(verbose_name="入浴",default=0,choices=bath_choice)
    wash_hair    = models.BooleanField(verbose_name="洗髪",default=False)
    #身体整容
    wash_face    = models.BooleanField(verbose_name="洗面",default=False)
    wash_mouse   = models.BooleanField(verbose_name="口腔ケア",default=False)
    makeup_nail  = models.BooleanField(verbose_name="整容（爪）",default=False)
    makeup_ear   = models.BooleanField(verbose_name="整容（耳）",default=False)
    makeup_beard = models.BooleanField(verbose_name="整容（髭）",default=False)
    makeup_hair  = models.BooleanField(verbose_name="整容（髪）",default=False)
    makeup_face  = models.BooleanField(verbose_name="整容（化粧）",default=False)
    change_cloth = models.BooleanField(verbose_name="更衣介助",default=False)
    #移動
    change_pos   = models.BooleanField(verbose_name="体位変換",default=False)
    movetransfer = models.BooleanField(verbose_name="移乗介助",default=False)
    move         = models.BooleanField(verbose_name="移動介助",default=False)
    readytomove  = models.BooleanField(verbose_name="外出準備介助",default=False)
    readytocome  = models.BooleanField(verbose_name="帰宅受入介助",default=False)
    gotohospital = models.BooleanField(verbose_name="通院介助",default=False)
    gotoshopping = models.BooleanField(verbose_name="買物介助",default=False)
    #起床就寝
    wakeup       = models.BooleanField(verbose_name="起床介助",default=False)
    goingtobed   = models.BooleanField(verbose_name="就寝介助",default=False)
    #服薬・医療行為
    medicine     = models.BooleanField(verbose_name="服薬介助・確認",default=False)
    medicine_app = models.BooleanField(verbose_name="薬の塗布",default=False)
    eye_drops    = models.BooleanField(verbose_name="点眼",default=False)
    #その他
    in_hospital  = models.BooleanField(verbose_name="院内介助",default=False)
    watch_over   = models.BooleanField(verbose_name="見守り",default=False)
    #自立支援
    jir_together = models.CharField(verbose_name="共に行う(内容)",max_length=50,default="",blank=True)
    jir_memory   = models.BooleanField(verbose_name="記憶への働きかけ",default=False)
    jir_call_out = models.BooleanField(verbose_name="声かけと見守り",default=False)
    jir_shopping = models.BooleanField(verbose_name="買物援助",default=False)
    jir_motivate = models.BooleanField(verbose_name="意欲関心の引き出し",default=False)

    #生活援助/////////////////////////////////////////////////////////////////////////////////////////////////
    #清掃
    cl_room      = models.BooleanField(verbose_name="居室",default=False)
    cl_toilet    = models.BooleanField(verbose_name="トイレ",default=False)
    cl_table     = models.BooleanField(verbose_name="卓上",default=False)
    cl_kitchen   = models.BooleanField(verbose_name="台所",default=False)
    cl_bath      = models.BooleanField(verbose_name="浴室",default=False)
    cl_p_toilet  = models.BooleanField(verbose_name="Pトイレ",default=False)
    cl_bedroom   = models.BooleanField(verbose_name="寝室",default=False)
    cl_hall      = models.BooleanField(verbose_name="廊下",default=False)
    cl_front     = models.BooleanField(verbose_name="玄関",default=False)
    cl_trush     = models.BooleanField(verbose_name="ゴミ出し",default=False)
    #洗濯
    washing      = models.BooleanField(verbose_name="洗濯",default=False)
    wash_dry     = models.BooleanField(verbose_name="乾燥(物干し)",default=False)
    wash_inbox   = models.BooleanField(verbose_name="取り入れ・収納",default=False)
    wash_iron    = models.BooleanField(verbose_name="アイロン",default=False)
    #寝具
    bed_change   = models.BooleanField(verbose_name="シーツ・カバー交換",default=False)
    bed_making   = models.BooleanField(verbose_name="ベッドメイク",default=False)
    bed_dry      = models.BooleanField(verbose_name="布団干し",default=False)
    #衣類
    cloth_sort   = models.BooleanField(verbose_name="衣類の整理",default=False)
    cloth_repair = models.BooleanField(verbose_name="被服の補修",default=False)
    #調理
    cooking      = models.BooleanField(verbose_name="調理",default=False)
    cook_lower   = models.BooleanField(verbose_name="下拵え",default=False)
    cook_prepare = models.BooleanField(verbose_name="配・下膳",default=False)
    cook_menu    = models.CharField(verbose_name="献立",max_length=50,default="",blank=True)
    #買物等
    daily_shop   = models.BooleanField(verbose_name="日常品等買物",default=False)
    Receive_mad  = models.BooleanField(verbose_name="薬の受取り",default=False)
    deposit      = models.PositiveIntegerField(verbose_name="預り金",default=0,blank=True)
    payment      = models.PositiveIntegerField(verbose_name="買物",default=0,blank=True)
    biko         = models.TextField(verbose_name="特記・連絡事項")

    created_by   = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name="登録スタッフ",on_delete=models.RESTRICT)
    created_at   = models.DateTimeField(verbose_name="登録日",auto_now_add=True)
    updated_at   = models.DateTimeField(verbose_name="更新日",auto_now=True)

    def __str__(self):
        return f"{self.schedule.careuser}" 


class ShowUserEnddate(models.Model):
    
    end_date       = models.DateTimeField(verbose_name="表示最終日時")
    updated_by     = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name="更新者",on_delete=models.RESTRICT)
    updated_at     = models.DateTimeField(verbose_name="更新日",auto_now=True)

    def __str__(self):
        return f"{self.end_date}" 