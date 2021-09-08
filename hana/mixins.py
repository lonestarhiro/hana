from django.contrib.auth.mixins import UserPassesTestMixin
import calendar
import datetime
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

    def get_month_calendar(self):
        """月間カレンダー情報の入った辞書を返す"""
        self.setup_calendar()
        current = self.get_current()
        calendar_data = {
            'now': datetime.date.today(),
            'month_days': self.get_month_days(current),
            'month_current': current,
            'month_previous': self.get_previous_month(current),
            'month_next': self.get_next_month(current),
            'week_names': self.get_week_names(),
        }
        return calendar_data


class MonthWithScheduleMixin(MonthCalendarMixin):
    """スケジュール付きの、月間カレンダーを提供するMixin"""

    def get_month_schedules(self, start, end, days):
        """それぞれの日とスケジュールを返す"""
        #ログイン中のユーザー
        login_user = self.request.user
        
        condition_date  = Q(start_date__range=[start,end])

        login_user = self.request.user
        condition_staff = (Q(staff1=login_user)|Q(staff2=login_user)|Q(staff3=login_user)|Q(staff4=login_user)|\
                           Q(tr_staff1=login_user)|Q(tr_staff2=login_user)|Q(tr_staff3=login_user)|Q(tr_staff4=login_user))
        queryset = self.model.objects.filter(condition_date,condition_staff).order_by(self.date_field)

        # {1日のdatetime: 1日のスケジュール全て, 2日のdatetime: 2日の全て...}のような辞書を作る
        day_schedules = {day: [] for week in days for day in week}
        for schedule in queryset:
            schedule_date = getattr(schedule,self.date_field)
            #dateに変換
            schedule_date = localtime(schedule_date).date()
            day_schedules[schedule_date].append(schedule)

        # day_schedules辞書を、周毎に分割する。[{1日: 1日のスケジュール...}, {8日: 8日のスケジュール...}, ...]
        # 7個ずつ取り出して分割しています。
        size = len(day_schedules)
        return [{key: day_schedules[key] for key in itertools.islice(day_schedules, i, i+7)} for i in range(0, size, 7)]

    def get_month_calendar(self):
        calendar_context = super().get_month_calendar()
        month_days = calendar_context['month_days']
        month_first = month_days[0][0]
        month_last = month_days[-1][-1]
        calendar_context['month_day_schedules'] = self.get_month_schedules(
            month_first,
            month_last,
            month_days
        )
        return calendar_context