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
from schedules.views import search_sametime_query,search_staff_tr_query
from urllib.parse import urlencode
from django.shortcuts import get_object_or_404


#以下SuperUserRequiredMixin
class ScheduleImportView(StaffUserRequiredMixin,View):

    def get(self,request):
        
        #日ごとのdict初期化
        days_list = {}

        #追加する日の期間を取得
        insert_days = self.get_insert_days()
        #追加するスケジュールを取得
        insert_defsches = self.get_insert_default_schedules(insert_days)
   
        #日毎のdictを作成し、defscheを追加していく
        for day in range(insert_days['insert_start_day'],insert_days['insert_end_day_for_range']):
            days_list[day] = []
            for defsche in insert_defsches:                
                if self.check_insert(day,defsche,insert_days):
                    days_list[day].append(defsche)

        #日毎にinsertしていく
        for day,defsches in days_list.items():
            for defsche in defsches:
                self.insert_schedule(defsche,insert_days['year'],insert_days['month'],day)

        #終了後リダイレクト
        if self.request.GET.get('def_sche',default=None):
            if len(insert_defsches):
                redirect_url = reverse('schedules:monthlylist',kwargs={'year':insert_days['year'] ,'month':insert_days['month']})
                parameters = urlencode(dict(careuser=insert_defsches[0].careuser.pk))
                ret = f'{redirect_url}?{parameters}'
                return HttpResponseRedirect(ret)

            return HttpResponseRedirect(reverse_lazy('careusers:list'))
        else:
            return HttpResponseRedirect(reverse('schedules:monthlylist', kwargs=dict(year=insert_days['year'],month=insert_days['month'])))

    def get_insert_days(self):
        nowtime = make_aware(datetime.datetime.today())
        if self.request.path == reverse('schedules:import'):
            year  = nowtime.year
            month = nowtime.month
        elif self.request.path == reverse('schedules:import_next'):
            next  = nowtime + relativedelta(months=1)
            year  = next.year
            month = next.month
       
        #セットする月の日数を取得
        total_days = calendar.monthrange(year,month)[1]

        ret_dict = {}
        ret_dict['year']                     = year
        ret_dict['month']                    = month
        ret_dict['insert_start_datetime']    = None
        ret_dict['insert_end_datetime']      = None
        ret_dict['insert_start_day']         = None
        ret_dict['insert_end_day']           = None
        ret_dict['insert_end_day_for_range'] = None
        
        #def_scheが指定されていたらそれのみ実行する
        if self.request.GET.get('def_sche',default=None):
            if self.request.GET.get('start_day',default=None):
                ret_dict['insert_start_day']      = int(self.request.GET.get('start_day'))
            else:
                ret_dict['insert_start_day'] = 1

            if self.request.GET.get('end_day',default=None):
                if int(self.request.GET.get('end_day')) > total_days:
                    ret_dict['insert_end_day'] = total_days                    
                else:
                    ret_dict['insert_end_day'] = int(self.request.GET.get('end_day')) 
            else:
                ret_dict['insert_end_day'] = total_days

            ret_dict['insert_start_datetime'] = make_aware(datetime.datetime(year,month,ret_dict['insert_start_day']))
            ret_dict['insert_end_datetime']   = make_aware(datetime.datetime(year,month,ret_dict['insert_end_day'])) + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
        #月次一括登録の場合
        elif self.request.user.is_superuser:           
            ret_dict['insert_start_day'] = 1
            ret_dict['insert_end_day'] = total_days
            ret_dict['insert_start_datetime'] = make_aware(datetime.datetime(year,month,1))
            ret_dict['insert_end_datetime']   = ret_dict['insert_start_datetime'] + relativedelta(months=1) - datetime.timedelta(seconds=1)


        ret_dict['insert_end_day_for_range'] = ret_dict['insert_end_day']+1
        return ret_dict

    def get_insert_default_schedules(self,insert_days):
        
        def_sche_dict = []
        #既に今月全体のimportされているかチェック用
        month_all_sche = Schedule.objects.filter(start_date__range=[insert_days['insert_start_datetime'],insert_days['insert_end_datetime']],def_sche__isnull=False)

        #def_scheが指定されていたらそれのみ実行する
        if self.request.GET.get('def_sche',default=None):
            #まだ月次の一括登録されていなければ登録をキャンセルする
            if month_all_sche:
                #文字列のリストを取り込む
                str_keys = self.request.GET.get('def_sche').split(",")
                for key in str_keys:
                    defsche = get_object_or_404(DefaultSchedule.objects.select_related('careuser'),pk=key,add_stop=False,careuser__is_active=True)
                    def_sche_dict.append(defsche)
        #月次一括登録の場合
        elif self.request.user.is_superuser:
                def_sche = DefaultSchedule.objects.select_related('careuser').filter(add_stop=False,careuser__is_active=True).order_by('careuser')
                #まだ全体のimportがされていなければ実行
                if month_all_sche.count()==0:
                    for defsche in def_sche:
                        def_sche_dict.append(defsche)

        return def_sche_dict

    def check_insert(self,day,defsche,insert_days):
        #曜日取得 0=月,1=火,2=水,3=木,4=金,5=土,6=日
        week = calendar.weekday(insert_days['year'], insert_days['month'], day)
        #第何回目の曜日か取得
        nth  = (day - 1) // 7 + 1

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


    def insert_schedule(self,defsche,year,month,day):
    
        #追加する日時を取得
        starttime = make_aware(datetime.datetime(year,month,day,defsche.start_h,defsche.start_m))
        endtime   = starttime + datetime.timedelta(minutes=defsche.service.time)

        #曜日取得 0=月,1=火,2=水,3=木,4=金,5=土,6=日
        week = calendar.weekday(year, month, day)

        #まず既に同じ利用者の同時間帯に登録がないかチェック###################################################################################################
        careuser_duplicate_check_obj = Schedule.objects.filter(search_sametime_query(starttime,endtime),careuser=defsche.careuser)
        careuser_check_level = 0

        #サービスの重複を除いたリストを作成
        careuser_dup_not_canceled_list = []
        
        for sche in careuser_duplicate_check_obj:
            if sche.cancel_flg ==False:
                careuser_dup_not_canceled_list.append(sche)
            if sche.def_sche==defsche:
                #既に同一のdef_scheからの登録がある場合は登録処理を中止
                return

        #キャンセルでないレコードが存在する場合
        if careuser_duplicate_check_obj:            
            careuser_check_level = 3
            #既存のレコードを更新
            for s in careuser_dup_not_canceled_list:
                s.careuser_check_level = 3
                s.save()


        #過去一カ月defスケジュールの同一曜日の履歴よりスタッフごとのサービス実績（回数）を取得########################################
        
        #スタッフをセットしないにチェックがある場合
        if defsche.no_set_staff:
            ins_staff_list =[None,None,None,None]
            staff_check_level = 2
        else:
            #先月の検索期間を設定
            search_from = make_aware(datetime.datetime(year,month,1)) - relativedelta(months=1)
            search_to   = make_aware(datetime.datetime(year,month,1)) - datetime.timedelta(seconds=1)

            staff_check_level = 0

            #スタッフごとのサービス実績（回数）を取得
            rank_staff_dict = {}

            #日付指定でない場合
            if not defsche.type==1 or not defsche.weektype==3:
                search_obj = Schedule.objects.select_related('staff1','staff2','staff3','staff4').filter(def_sche=defsche,cancel_flg=False,start_date__range=(search_from,search_to),start_date__iso_week_day=week+1)
            #日付指定の場合
            else:
                search_obj = Schedule.objects.select_related('staff1','staff2','staff3','staff4').filter(def_sche=defsche,cancel_flg=False,start_date__range=(search_from,search_to),start_date__day=day)
            
            for sche in search_obj:
                if sche.staff1 and sche.peoples>=1:
                    if sche.staff1 in rank_staff_dict:
                        rank_staff_dict[sche.staff1] += 1
                    else:
                        rank_staff_dict[sche.staff1] = 1
                if sche.staff2 and sche.peoples>=2:
                    if sche.staff2 in rank_staff_dict:
                        rank_staff_dict[sche.staff2] += 1
                    else:
                        rank_staff_dict[sche.staff2] = 1
                if sche.staff3 and sche.peoples>=3:
                    if sche.staff3 in rank_staff_dict:
                        rank_staff_dict[sche.staff3] += 1
                    else:
                        rank_staff_dict[sche.staff3] = 1
                if sche.staff4 and sche.peoples>=4:
                    if sche.staff4 in rank_staff_dict:
                        rank_staff_dict[sche.staff4] += 1
                    else:
                        rank_staff_dict[sche.staff4] = 1

            rank_staff_dict = sorted(rank_staff_dict.items(),key=lambda x:x[1], reverse=True)
            print(rank_staff_dict)
            #履歴の多いスタッフ順にスケジュールの空きをチェックし、空いていればリストに登録############################################################################
            sche_ok_staff_list = []

            for staff in rank_staff_dict:
                staff_duplicate_check_obj = Schedule.objects.filter(search_sametime_query(starttime,endtime),search_staff_tr_query(staff[0]),cancel_flg=False)
                if not staff_duplicate_check_obj:
                    sche_ok_staff_list.append(staff[0])

            #上記のリストよりスタッフをセット
            ins_staff_list = []

            for cnt in range(4):
                if cnt < defsche.peoples:
                    if cnt < len(sche_ok_staff_list):
                        ins_staff_list.append(sche_ok_staff_list[cnt])
                    else:
                        ins_staff_list.append(None)
                        if staff_check_level < 2:
                            staff_check_level = 2
                else:
                    ins_staff_list.append(None)

        #Schedule に追記
        obj = Schedule(careuser=defsche.careuser,start_date=starttime,end_date=endtime,service=defsche.service,peoples=defsche.peoples,\
                      staff1=ins_staff_list[0],staff2=ins_staff_list[1],staff3=ins_staff_list[2],staff4=ins_staff_list[3],\
                                  biko=defsche.biko,def_sche=defsche,careuser_check_level=careuser_check_level,staff_check_level=staff_check_level,cancel_flg=False,created_by=self.request.user)
        obj.save()
        
        #実績記録(Report)レコードを作成
        Report.objects.create(schedule=obj,created_by=self.request.user)

