from django.http import HttpResponseRedirect
from django.db.models import Q
from schedules.models import Schedule
from staffs.models import User
from careusers.models import CareUser,DefaultSchedule
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse
from django.views.generic import View
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware
import collections


#以下staffuserのみ表示（下のStaffUserRequiredMixinにて制限中）
class ScheduleImportView(StaffUserRequiredMixin,View):

    def get(self,request):
        #model = Schedule
        if request.path == reverse('schedules:import'):
            year = datetime.datetime.today().year
            month = datetime.datetime.today().month
        elif request.path == reverse('schedules:import_next'):
            next = datetime.datetime.today() + relativedelta(months=1)
            year = next.year
            month = next.month

        
        #セットする月の日数を取得
        total_days = self.month_days(year,month)

        def_sche = DefaultSchedule.objects.select_related('careuser').all().filter(careuser__is_active=True).order_by('careuser')

        for day in range(1,int(total_days)+1):

            #曜日取得 0=月,1=火,2=水,3=木,4=金,5=土,6=日
            week = self.get_week(year, month, day)

            #第何回目の曜日か取得
            nth = self.get_nth_cnt(day)

            for defsche in def_sche:
                #var = defsche.get_schedule_name() + defsche.get_start_time() + "～" + defsche.get_end_time() + defsche.careuser.last_name
                #print(var)

                #週ベースの登録の場合
                #[(0,"毎週"),(1,"隔週1-3-5"),(2,"隔週2-4"),(3,"第1"),(4,"第2"),(5,"第3"),(6,"第4")]
                if defsche.type==0:
                    
                    if defsche.weektype==0:
                        if (defsche.mon and week==0) or\
                           (defsche.tue and week==1) or\
                           (defsche.wed and week==2) or\
                           (defsche.thu and week==3) or\
                           (defsche.fri and week==4) or\
                           (defsche.sat and week==5) or\
                           (defsche.sun and week==6):

                            self.insert_schedule(defsche,year,month,day)

                    elif defsche.weektype==1:
                        if (defsche.mon and week==0 and nth%2==1) or\
                           (defsche.tue and week==1 and nth%2==1) or\
                           (defsche.wed and week==2 and nth%2==1) or\
                           (defsche.thu and week==3 and nth%2==1) or\
                           (defsche.fri and week==4 and nth%2==1) or\
                           (defsche.sat and week==5 and nth%2==1) or\
                           (defsche.sun and week==6 and nth%2==1):

                            self.insert_schedule(defsche,year,month,day)

                    elif defsche.weektype==2:
                        if (defsche.mon and week==0 and nth%2==0) or\
                           (defsche.tue and week==1 and nth%2==0) or\
                           (defsche.wed and week==2 and nth%2==0) or\
                           (defsche.thu and week==3 and nth%2==0) or\
                           (defsche.fri and week==4 and nth%2==0) or\
                           (defsche.sat and week==5 and nth%2==0) or\
                           (defsche.sun and week==6 and nth%2==0):

                            self.insert_schedule(defsche,year,month,day)

                    elif defsche.weektype==3:
                        if (defsche.mon and week==0 and nth==1) or\
                           (defsche.tue and week==1 and nth==1) or\
                           (defsche.wed and week==2 and nth==1) or\
                           (defsche.thu and week==3 and nth==1) or\
                           (defsche.fri and week==4 and nth==1) or\
                           (defsche.sat and week==5 and nth==1) or\
                           (defsche.sun and week==6 and nth==1):

                            self.insert_schedule(defsche,year,month,day)

                    elif defsche.weektype==4:
                        if (defsche.mon and week==0 and nth==2) or\
                           (defsche.tue and week==1 and nth==2) or\
                           (defsche.wed and week==2 and nth==2) or\
                           (defsche.thu and week==3 and nth==2) or\
                           (defsche.fri and week==4 and nth==2) or\
                           (defsche.sat and week==5 and nth==2) or\
                           (defsche.sun and week==6 and nth==2):

                            self.insert_schedule(defsche,year,month,day)

                    elif defsche.weektype==5:
                        if (defsche.mon and week==0 and nth==3) or\
                           (defsche.tue and week==1 and nth==3) or\
                           (defsche.wed and week==2 and nth==3) or\
                           (defsche.thu and week==3 and nth==3) or\
                           (defsche.fri and week==4 and nth==3) or\
                           (defsche.sat and week==5 and nth==3) or\
                           (defsche.sun and week==6 and nth==3):

                            self.insert_schedule(defsche,year,month,day)

                    elif defsche.weektype==6:
                        if (defsche.mon and week==0 and nth==4) or\
                           (defsche.tue and week==1 and nth==4) or\
                           (defsche.wed and week==2 and nth==4) or\
                           (defsche.thu and week==3 and nth==4) or\
                           (defsche.fri and week==4 and nth==4) or\
                           (defsche.sat and week==5 and nth==4) or\
                           (defsche.sun and week==6 and nth==4):

                            self.insert_schedule(defsche,year,month,day)

                #日ベースの登録の場合
                #[(0,"毎日"),(1,"奇数日"),(2,"偶数日"),(3,"日付指定")]
                elif defsche.type==1:

                    if defsche.daytype==0:
                        self.insert_schedule(defsche,year,month,day)
                    
                    elif defsche.daytype==1:
                        if day%2 ==1:
                            self.insert_schedule(defsche,year,month,day)
                    
                    elif defsche.daytype==2:
                        if day%2 ==0:
                            self.insert_schedule(defsche,year,month,day)
                    
                    elif defsche.daytype==3:
                        if day==defsche.day:
                            self.insert_schedule(defsche,year,month,day)
                
            #print(str(month) + "月" + str(day) + "日")
        return HttpResponseRedirect(reverse('schedules:monthlylist', kwargs=dict(year=year,month=month)))

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
        #print(str(starttime) + " " + str(endtime) + " " + defsche.careuser.last_name)


        #まず既に同じ利用者の同時間帯に登録がないかチェック###################################################################################################
        careuser_duplicate_check_obj = Schedule.objects.filter(Q(careuser=defsche.careuser),(Q(start_date__lte=starttime,end_date__gt=starttime) | Q(start_date__lt=endtime,end_date__gte=endtime)))
        
        if careuser_duplicate_check_obj.count() > 0:
            check_flg=True

        #既に同一のdef_scheからの登録がある場合は登録処理を中止
        if careuser_duplicate_check_obj.filter(def_sche_id=defsche.pk):
            return

        #defスケジュールの履歴（pkにて絞り込み）よりサービス可能スタッフごとのサービス実績（回数）を取得##########################################################
        
        #検索期間を設定
        search_from = datetime.datetime(year,month,1) - relativedelta(months=2)
        search_to   = datetime.datetime(year,month,1) - datetime.timedelta(seconds=1)
        search_from = make_aware(search_from)
        search_to   = make_aware(search_to)

        rank_staff_dict = {}
        check_flg = False

        #スタッフごとのサービス実績（回数）を取得
        for staff in defsche.staffs.all():

            search_obj = Schedule.objects.all().filter(Q(careuser=defsche.careuser,def_sche_id=defsche.pk,start_date__range=(search_from,search_to)),\
                         (Q(staff1=staff)|Q(staff2=staff)|Q(staff3=staff)|Q(staff4=staff)))

            rank_staff_dict[staff.pk] =search_obj.count()

        rank_staff_dict = sorted(rank_staff_dict.items(),key=lambda x:x[1], reverse=True)

        #履歴の多いスタッフ順にスケジュールの空きをチェックし、空いていればリストに登録############################################################################

        sche_ok_staff_list = list()

        for staff in rank_staff_dict:
            staff_duplicate_check_obj = Schedule.objects.all().filter((Q(start_date__lte=starttime,end_date__gt=starttime) | Q(start_date__lt=endtime,end_date__gte=endtime)),\
                                        (Q(staff1=staff)|Q(staff2=staff)|Q(staff3=staff)|Q(staff4=staff)))
            if staff_duplicate_check_obj.count() == 0:
                sche_ok_staff_list.append(staff[0])


        #上記のリストよりスタッフをセット
        ins_staff_list = []
        
        for cnt in range(4):
            if(cnt < defsche.peoples):
                if(cnt < len(sche_ok_staff_list)):
                    ins_staff_list[cnt] = sche_ok_staff_list[cnt]
                else:
                     ins_staff_list[cnt] =""
            else:
                ins_staff_list[cnt] =""

        #Schedule に追記
        obj = Schedule(careuser=defsche.careuser,start_date=starttime,end_date=endtime,service=defsche.service,peoples=defsche.peoples,\
                      staff1=User(id=ins_staff_list[0]),staff2=User(id=ins_staff_list[1]),staff3=User(id=ins_staff_list[2]),staff4=User(id=ins_staff_list[3]),biko=defsche.biko,def_sche_id=defsche.pk,\
                      check_flg=check_flg,comfirm_flg=False,created_by=self.request.user)
        obj.save()
