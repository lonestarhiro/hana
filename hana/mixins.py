from django.contrib.auth.mixins import UserPassesTestMixin
import calendar
import datetime
from staffs.models import User
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
            if get_staff is not None:
                selected_staff = User.objects.get(pk=get_staff)
            else:
                selected_staff = None
        else:
            selected_staff = User.objects.get(pk=self.request.user)
        return selected_staff

    def get_careuser(self):
        """表示する利用者を返す"""
        get_careuser = self.request.GET.get('careuser')
        if get_careuser is not None:
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
        if staff_obj is None and careuser_obj is None:
            condition_people = Q()
        elif staff_obj is not None:
            condition_people = (Q(staff1=staff_obj)|Q(staff2=staff_obj)|Q(staff3=staff_obj)|Q(staff4=staff_obj)|\
                               Q(tr_staff1=staff_obj)|Q(tr_staff2=staff_obj)|Q(tr_staff3=staff_obj)|Q(tr_staff4=staff_obj))
        elif careuser_obj is not None:
            condition_people = Q(careuser=careuser_obj)
        
        queryset = self.model.objects.filter(condition_date,condition_people).order_by(self.order_date_field)

        # {1日のdatetime: 1日のスケジュール全て, 2日のdatetime: 2日の全て...}のような辞書を作る
        day_schedules = {day: [] for week in days for day in week}
        for schedule in queryset:
            schedule_date = getattr(schedule,self.order_date_field)
            #dateに変換
            schedule_date = localtime(schedule_date).date()
            day_schedules[schedule_date].append(schedule)

        # day_schedules辞書を、周毎に分割する。[{1日: 1日のスケジュール...}, {8日: 8日のスケジュール...}, ...]
        # 7個ずつ取り出して分割しています。
        size = len(day_schedules)
        return [{key: day_schedules[key] for key in itertools.islice(day_schedules, i, i+7)} for i in range(0, size, 7)]

    def get_month_data(self):
        calendar_context = super().get_month_calendar()
        month_days  = calendar_context['month_days']
        month_first = month_days[0][0]
        month_last  = month_days[-1][-1]
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