from django.contrib.auth.mixins import UserPassesTestMixin
import calendar
import datetime
from staffs.models import User
from schedules.models import ShowUserEnddate
from careusers.models import CareUser
from collections import deque
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware,localtime
import itertools
from django.db.models import Q

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class StaffUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class BaseCalendarMixin:
    """カレンダー関連Mixinの、基底クラス"""
    first_weekday = 6  # 0は月曜から、1は火曜から。6なら日曜日からになります。お望みなら、継承したビューで指定してください。
    week_names = ['月', '火', '水', '木', '金', '土', '日']  # これは、月曜日から書くことを想定します。['Mon', 'Tue'...

    def setup_calendar(self):
        """内部カレンダーの設定処理
        calendar.Calendarクラスの機能を利用するため、インスタンス化します。
        Calendarクラスのmonthdatescalendarメソッドを利用していますが、デフォルトが月曜日からで、
        火曜日から表示したい(first_weekday=1)、といったケースに対応するためのセットアップ処理です。
        """
        self._calendar = calendar.Calendar(self.first_weekday)

    def get_week_names(self):
        """first_weekday(最初に表示される曜日)にあわせて、week_namesをシフトする"""
        week_names = deque(self.week_names)
        week_names.rotate(-self.first_weekday)  # リスト内の要素を右に1つずつ移動...なんてときは、dequeを使うと中々面白いです
        return week_names

class MonthCalendarMixin(BaseCalendarMixin):
    """月間カレンダーの機能を提供するMixin"""

    def get_previous_month(self, date):
        """前月を返す"""
        
        return datetime.datetime(date.year,date.month,1) - relativedelta(months=1)

    def get_next_month(self, date):
        """次月を返す"""
        return datetime.datetime(date.year,date.month,1) + relativedelta(months=1)

    def get_month_days(self, date):
        """その月の全ての日を返す"""
        return self._calendar.monthdatescalendar(date.year, date.month)

    def get_current(self):
        """現在の月を返す"""
        if self.kwargs.get('year')==None or self.kwargs.get('month')==None:
            year  = datetime.datetime.today().year
            month = datetime.datetime.today().month
        else:
            year = self.kwargs.get('year')
            month= self.kwargs.get('month')

        date = datetime.datetime(year,month,1)
        date = make_aware(date)
        return date

    def get_staff(self):
        """表示するユーザーを返す"""
        #is_staff権限のないスタッフには全体のスケジュールを表示しない。
        if self.request.user.is_staff:
            get_staff = self.request.GET.get('staff')
            if get_staff:
                selected_staff = User.objects.get(pk=get_staff)
            else:
                selected_staff = None
        else:
            selected_staff = User.objects.get(pk=self.request.user.pk)
        return selected_staff

    def get_careuser(self):
        """表示する利用者を返す"""
        get_careuser = self.request.GET.get('careuser')
        if get_careuser:
            selected_careuser = CareUser.objects.get(pk=get_careuser)
        else:
            selected_careuser = None

        return selected_careuser

    def jpholidays(self):
        #内閣府のhttps://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html　からcsvをダウンロードしエクセルで複数行をコピーし
        #ここにペーストしたら日付を抜きとれる
        holiday =('2021/8/8','2021/8/9','2021/9/20','2021/9/23','2021/11/3','2021/11/23','2022/1/1','2022/1/10','2022/2/11','2022/2/23','2022/3/21',\
                  '2022/4/29','2022/5/3','2022/5/4','2022/5/5','2022/7/18','2022/8/11','2022/9/19','2022/9/23','2022/10/10','2022/11/3','2022/11/23')
        return holiday;

    def get_month_calendar(self):
        """月間カレンダー情報の入った辞書を返す"""
        self.setup_calendar()
        current = self.get_current()
        calendar_data = {
            'now': datetime.date.today(),
            'month_days': self.get_month_days(current),
            'month_current': current,
            'holidays':self.jpholidays,
            'month_previous': self.get_previous_month(current),
            'month_next': self.get_next_month(current),
            'week_names': self.get_week_names(),
            'staff_obj': self.get_staff(),
            'careuser_obj': self.get_careuser(),
        }
        return calendar_data

class MonthWithScheduleMixin(MonthCalendarMixin):
    """スケジュール付きの、月間カレンダーを提供するMixin"""

    def get_month_schedules(self, start, end, days ,staff_obj,careuser_obj):
        """それぞれの日とスケジュールを返す"""
        condition_date  = Q(start_date__range=[start,end])
        if self.request.user.is_staff:
            if staff_obj is None and careuser_obj is None:
                condition_people = Q()
            elif staff_obj:
                condition_people = (Q(staff1=staff_obj)|Q(staff2=staff_obj)|Q(staff3=staff_obj)|Q(staff4=staff_obj)|\
                                Q(tr_staff1=staff_obj)|Q(tr_staff2=staff_obj)|Q(tr_staff3=staff_obj)|Q(tr_staff4=staff_obj))
            elif careuser_obj:
                condition_people = Q(careuser=careuser_obj)

            condition_show  = Q()
        else:
            condition_people = (Q(staff1=self.request.user)|Q(staff2=self.request.user)|Q(staff3=self.request.user)|Q(staff4=self.request.user)|\
                                Q(tr_staff1=self.request.user)|Q(tr_staff2=self.request.user)|Q(tr_staff3=self.request.user)|Q(tr_staff4=self.request.user))
            #登録ヘルパーへの表示最終日時
            if ShowUserEnddate.objects.all().count()>0:
                show_enddate = ShowUserEnddate.objects.first().end_date
            else:
                show_enddate = datetime.datetime(1970,1,1)
                show_enddate = make_aware(show_enddate)
        
            #登録ヘルパーには表示許可が出てからスケジュールを表示する
            condition_show  = Q(start_date__lte =show_enddate)
        
        queryset = self.model.objects.select_related('careuser','staff1','staff2','staff3','staff4','tr_staff1','tr_staff2','tr_staff3','tr_staff4').filter(condition_date,condition_people,condition_show).order_by('start_date')

        # {1日のdatetime: 1日のスケジュール全て, 2日のdatetime: 2日の全て...}のような辞書を作る
        day_schedules = {day: [] for week in days for day in week}

        for schedule in queryset:
            schedule_date = schedule.start_date
            #dateに変換
            schedule_date = localtime(schedule_date).date()

            #開始時刻と終了時刻が繋がるかつ、同一スタッフのリストがあればスケジュールを繋げ、一つに時刻を修正する。
            edit_flg = False
            #当日内スケジュールの比較
            for sche in day_schedules[schedule_date]:
                #scheとschedule共にlocaltime化前の状態での比較・処理
                if (sche.start_date == schedule.end_date or sche.end_date == schedule.start_date) \
                    and sche.careuser == schedule.careuser and sche.cancel_flg == schedule.cancel_flg \
                    and sche.staff1 == schedule.staff1 and sche.staff2 == schedule.staff2 \
                    and sche.staff3 == schedule.staff3 and sche.staff4 == schedule.staff4 \
                    and sche.tr_staff1 == schedule.tr_staff1 and sche.tr_staff2 == schedule.tr_staff2 \
                    and sche.tr_staff3 == schedule.tr_staff3 and sche.tr_staff4 == schedule.tr_staff4 :
                    #既にリストに追加されている時刻を上書き
                    if sche.start_date > schedule.start_date:
                        sche.start_date = schedule.start_date
                        edit_flg = True
                    if sche.end_date < schedule.end_date:
                        sche.end_date = schedule.end_date
                        edit_flg = True

            #前日24時までのスケジュールと０時からのスケジュールも繋げる
            yesterday = schedule_date - datetime.timedelta(1)
            if yesterday in day_schedules:
                #ローカルタイムでの0時を作成
                schedule_date_0oc = make_aware(datetime.datetime.combine(schedule_date,datetime.time()))
                for sche in day_schedules[yesterday]:
                    if sche.end_date == schedule_date_0oc and schedule.start_date == schedule_date_0oc \
                        and sche.careuser == schedule.careuser and sche.cancel_flg == schedule.cancel_flg \
                        and sche.staff1 == schedule.staff1 and sche.staff2 == schedule.staff2 \
                        and sche.staff3 == schedule.staff3 and sche.staff4 == schedule.staff4 \
                        and sche.tr_staff1 == schedule.tr_staff1 and sche.tr_staff2 == schedule.tr_staff2 \
                        and sche.tr_staff3 == schedule.tr_staff3 and sche.tr_staff4 == schedule.tr_staff4 :

                        if sche.end_date < schedule.end_date:
                            sche.end_date = schedule.end_date
                            edit_flg = True

            #上記で時刻の上書きがない場合はリストに追加。
            if edit_flg is False:
                day_schedules[schedule_date].append(schedule)

        # day_schedules辞書を、周毎に分割する。[{1日: 1日のスケジュール...}, {8日: 8日のスケジュール...}, ...]
        # 7個ずつ取り出して分割しています。
        size = len(day_schedules)
        return [{key: day_schedules[key] for key in itertools.islice(day_schedules, i, i+7)} for i in range(0, size, 7)]

    def get_month_data(self):
        calendar_context = super().get_month_calendar()
        month_days  = calendar_context['month_days']
        month_first = datetime.datetime.combine(month_days[0][0],datetime.time())
        month_last  = datetime.datetime.combine(month_days[-1][-1] + datetime.timedelta(days=1),datetime.time()) - datetime.timedelta(seconds=1)
        month_first = make_aware(month_first)
        month_last  = make_aware(month_last)

        staff_obj   = calendar_context['staff_obj']
        careuser_obj= calendar_context['careuser_obj']
 
        calendar_context['month_day_schedules'] = self.get_month_schedules(
            month_first,
            month_last,
            month_days,
            staff_obj,
            careuser_obj,
        )
        return calendar_context