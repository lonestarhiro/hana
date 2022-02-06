from django.http import HttpResponseRedirect,Http404
from django.db.models import Q,Max
from schedules.models import Schedule,Report
from staffs.models import User
from careusers.models import DefaultSchedule
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse,reverse_lazy
from django.views.generic import View
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware,localtime
from schedules.views import search_sametime_query,search_staff_tr_query,booking_sametime_compare
from urllib.parse import urlencode
from django.shortcuts import get_object_or_404


#以下SuperUserRequiredMixin
class ScheduleImportView(StaffUserRequiredMixin,View):

    def get(self,request):
        nowtime = make_aware(datetime.datetime.today())
        if request.path == reverse('schedules:import'):
            year  = nowtime.year
            month = nowtime.month
        elif request.path == reverse('schedules:import_next'):
            next  = nowtime + relativedelta(months=1)
            year  = next.year
            month = next.month

        #今回生成する月の月初
        this_month = make_aware(datetime.datetime(year,month,1))
        next_month = this_month + relativedelta(months=1)

        #セットする月の日数を取得
        total_days = self.month_days(year,month)

        #既に今月全体のimportされているかチェック用
        month_all_sche = Schedule.objects.filter(start_date__range=[this_month,next_month],def_sche__isnull=False)

        #def_scheが指定されていたらそれのみ実行する
        if self.request.GET.get('def_sche',default=None):
            #まだ月次の一括登録されていなければ登録をキャンセルする
            if month_all_sche:
                #文字列のリストを取り込む
                str_keys = self.request.GET.get('def_sche').split(",")
                def_sche_keys = []
                for key in str_keys:
                    def_sche_keys.append(int(key))

                if self.request.GET.get('start_day',default=None):
                    insert_start_day = int(self.request.GET.get('start_day'))
                else:
                    insert_start_day = this_month.day

                if self.request.GET.get('end_day',default=None):
                    if int(self.request.GET.get('end_day')) > total_days:
                        insert_end_day = total_days+1
                    else:
                        insert_end_day = int(self.request.GET.get('end_day'))+1
                else:
                    insert_end_day = total_days+1

                for def_sche_key in def_sche_keys:
                    def_sche_obj = get_object_or_404(DefaultSchedule.objects.select_related('careuser'),pk=def_sche_key,careuser__is_active=True)
                    if def_sche_obj:
                        for day in range(insert_start_day,insert_end_day):
                            if self.check_insert(def_sche_obj,year, month, day):
                                #スケジュールの重複は以下のmethod内で防止される
                                self.insert_schedule(def_sche_obj,year,month,day)
                redirect_url = reverse('schedules:monthlylist',kwargs={'year':year ,'month':month})
                parameters = urlencode(dict(careuser=def_sche_obj.careuser.pk))
                ret = f'{redirect_url}?{parameters}'

                return HttpResponseRedirect(ret)

            return HttpResponseRedirect(reverse_lazy('careusers:list'))
        else:
            if self.request.user.is_superuser:
                def_sche = DefaultSchedule.objects.select_related('careuser').filter(add_stop=False,careuser__is_active=True).order_by('careuser')
                #まだ全体のimportがされていなければ実行
                if month_all_sche.count() ==0:
                    for day in range(1,int(total_days)+1):
                        for defsche in def_sche:
                            if self.check_insert(defsche,year, month, day):
                                self.insert_schedule(defsche,year,month,day)

            return HttpResponseRedirect(reverse('schedules:monthlylist', kwargs=dict(year=year,month=month)))

    def check_insert(self,defsche,year, month, day):
        #曜日取得 0=月,1=火,2=水,3=木,4=金,5=土,6=日
        week = self.get_week(year, month, day)
        #第何回目の曜日か取得
        nth  = self.get_nth_cnt(day)

        #週ベースの登録の場合
        #[(0,"毎週"),(1,"隔週1-3-5"),(2,"隔週2-4"),(3,"第1"),(4,"第2"),(5,"第3"),(6,"第4"),(7,"第5")]
        if defsche.type==0:
            if defsche.weektype==0:
                if (defsche.mon and week==0) or\
                    (defsche.tue and week==1) or\
                    (defsche.wed and week==2) or\
                    (defsche.thu and week==3) or\
                    (defsche.fri and week==4) or\
                    (defsche.sat and week==5) or\
                    (defsche.sun and week==6):
                    return True
            elif defsche.weektype==1:
                if (defsche.mon and week==0 and nth%2==1) or\
                    (defsche.tue and week==1 and nth%2==1) or\
                    (defsche.wed and week==2 and nth%2==1) or\
                    (defsche.thu and week==3 and nth%2==1) or\
                    (defsche.fri and week==4 and nth%2==1) or\
                    (defsche.sat and week==5 and nth%2==1) or\
                    (defsche.sun and week==6 and nth%2==1):
                    return True
            elif defsche.weektype==2:
                if (defsche.mon and week==0 and nth%2==0) or\
                    (defsche.tue and week==1 and nth%2==0) or\
                    (defsche.wed and week==2 and nth%2==0) or\
                    (defsche.thu and week==3 and nth%2==0) or\
                    (defsche.fri and week==4 and nth%2==0) or\
                    (defsche.sat and week==5 and nth%2==0) or\
                    (defsche.sun and week==6 and nth%2==0):
                    return True
            elif defsche.weektype==3:
                if (defsche.mon and week==0 and nth==1) or\
                    (defsche.tue and week==1 and nth==1) or\
                    (defsche.wed and week==2 and nth==1) or\
                    (defsche.thu and week==3 and nth==1) or\
                    (defsche.fri and week==4 and nth==1) or\
                    (defsche.sat and week==5 and nth==1) or\
                    (defsche.sun and week==6 and nth==1):
                    return True
            elif defsche.weektype==4:
                if (defsche.mon and week==0 and nth==2) or\
                    (defsche.tue and week==1 and nth==2) or\
                    (defsche.wed and week==2 and nth==2) or\
                    (defsche.thu and week==3 and nth==2) or\
                    (defsche.fri and week==4 and nth==2) or\
                    (defsche.sat and week==5 and nth==2) or\
                    (defsche.sun and week==6 and nth==2):
                    return True
            elif defsche.weektype==5:
                if (defsche.mon and week==0 and nth==3) or\
                    (defsche.tue and week==1 and nth==3) or\
                    (defsche.wed and week==2 and nth==3) or\
                    (defsche.thu and week==3 and nth==3) or\
                    (defsche.fri and week==4 and nth==3) or\
                    (defsche.sat and week==5 and nth==3) or\
                    (defsche.sun and week==6 and nth==3):
                    return True
            elif defsche.weektype==6:
                if (defsche.mon and week==0 and nth==4) or\
                    (defsche.tue and week==1 and nth==4) or\
                    (defsche.wed and week==2 and nth==4) or\
                    (defsche.thu and week==3 and nth==4) or\
                    (defsche.fri and week==4 and nth==4) or\
                    (defsche.sat and week==5 and nth==4) or\
                    (defsche.sun and week==6 and nth==4):
                    return True
            elif defsche.weektype==7:
                if (defsche.mon and week==0 and nth==5) or\
                    (defsche.tue and week==1 and nth==5) or\
                    (defsche.wed and week==2 and nth==5) or\
                    (defsche.thu and week==3 and nth==5) or\
                    (defsche.fri and week==4 and nth==5) or\
                    (defsche.sat and week==5 and nth==5) or\
                    (defsche.sun and week==6 and nth==5):
                    return True

        #日ベースの登録の場合
        #[(0,"毎日"),(1,"奇数日"),(2,"偶数日"),(3,"日付指定")]
        elif defsche.type==1:
            if defsche.daytype==0:
                return True
            elif defsche.daytype==1:
                if day%2 ==1:
                    return True
            elif defsche.daytype==2:
                if day%2 ==0:
                    return True
            elif defsche.daytype==3:
                if day==defsche.day:
                    return True

        return False

    #第〇週を取得
    def get_nth_cnt(self,day):
        return (day - 1) // 7 + 1

    #曜日取得
    def get_week(self,year, month, day):
        return calendar.weekday(year, month, day)

    def month_days(self,year,month):    
        return(calendar.monthrange(year,month)[1])

    def insert_schedule(self,defsche,year,month,day):

        #追加する日時を取得
        starttime = datetime.datetime(year,month,day,defsche.start_h,defsche.start_m)
        endtime   = starttime + datetime.timedelta(minutes=defsche.service.time)
        starttime = make_aware(starttime)
        endtime   = make_aware(endtime)

        #まず既に同じ利用者の同時間帯に登録がないかチェック###################################################################################################
        careuser_duplicate_check_obj = Schedule.objects.filter(search_sametime_query(starttime,endtime),careuser=defsche.careuser)
        careuser_check_level = 0

        #サービスの重複を除いたリストを作成
        careuser_dup_not_canceled_list = []
        careuser_dup_def_same_list = []
        
        for sche in careuser_duplicate_check_obj:
            if sche.cancel_flg ==False:
                careuser_dup_not_canceled_list.append(sche)
            if sche.def_sche==defsche:
                careuser_dup_def_same_list.append(sche)
       
        #既に同一のdef_scheからの登録がある場合は登録処理を中止
        if careuser_dup_def_same_list:
            return
        
        if careuser_duplicate_check_obj:
            #キャンセルでないレコードが存在する場合
            careuser_check_level = 3
            #既存のレコードを更新
            if careuser_dup_not_canceled_list:
                for s in careuser_dup_not_canceled_list:
                    s.careuser_check_level = 3
                    s.save()


        #過去一カ月defスケジュールの履歴よりサービス可能スタッフごとのサービス実績（回数）を取得########################################
        
        if defsche.no_set_staff:
            ins_staff_list =["","","",""]
            staff_check_level = 2
        else:
            #検索期間を設定
            search_from = datetime.datetime(year,month,1) - relativedelta(months=1)
            search_to   = datetime.datetime(year,month,1) - datetime.timedelta(seconds=1)
            search_from = make_aware(search_from)
            search_to   = make_aware(search_to)

            staff_check_level = 0

            #スタッフごとのサービス実績（回数）を取得
            rank_staff_dict = {}
            for staff in User.objects.filter(is_active=True,kaigo=True):

                search_obj = Schedule.objects.filter((Q(staff1=staff)|Q(staff2=staff)|Q(staff3=staff)|Q(staff4=staff)),def_sche=defsche,start_date__range=(search_from,search_to))

                if(search_obj.count()>0):
                    rank_staff_dict[staff.pk] =search_obj.count()
    
            rank_staff_dict = sorted(rank_staff_dict.items(),key=lambda x:x[1], reverse=True)

            #履歴の多いスタッフ順にスケジュールの空きをチェックし、空いていればリストに登録############################################################################
            sche_ok_staff_list = []

            for staff in rank_staff_dict:
                staff_duplicate_check_obj = Schedule.objects.filter(search_sametime_query(starttime,endtime),search_staff_tr_query(staff),cancel_flg=False)
                if staff_duplicate_check_obj.count() == 0:
                    sche_ok_staff_list.append(staff[0])

            #上記のリストよりスタッフをセット
            ins_staff_list = []

            for cnt in range(4):
                if(cnt < defsche.peoples):
                    if(cnt < len(sche_ok_staff_list)):
                        ins_staff_list.append(sche_ok_staff_list[cnt])
                    else:
                        ins_staff_list.append("")
                        if staff_check_level < 2:
                            staff_check_level = 2
                else:
                    ins_staff_list.append("")

        #Schedule に追記
        obj = Schedule(careuser=defsche.careuser,start_date=starttime,end_date=endtime,service=defsche.service,peoples=defsche.peoples,\
                      staff1=User(id=ins_staff_list[0]),staff2=User(id=ins_staff_list[1]),staff3=User(id=ins_staff_list[2]),staff4=User(id=ins_staff_list[3]),\
                                  biko=defsche.biko,def_sche=defsche,careuser_check_level=careuser_check_level,staff_check_level=staff_check_level,cancel_flg=False,created_by=self.request.user)
        obj.save()
        
        #実績記録(Report)レコードを作成
        Report.objects.create(schedule=obj,created_by=self.request.user)
