from django.contrib.auth.mixins import UserPassesTestMixin
import calendar
import datetime
from staffs.models import User
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
        if self.request.user.is_staff:
            get_staff = self.request.GET.get('staff')
            if get_staff is not None:
                selected_user = User.objects.get(pk=get_staff)
            else:
                selected_user = None
        else:
            selected_user = User.objects.get(pk=self.request.user)
        return selected_user

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
        }
        return calendar_data

class MonthWithScheduleMixin(MonthCalendarMixin):
    """スケジュール付きの、月間カレンダーを提供するMixin"""

    def get_month_schedules(self, start, end, days ,show_user):
        """それぞれの日とスケジュールを返す"""
        
        condition_date  = Q(start_date__range=[start,end])
        if show_user is None:
            condition_staff = Q()
        else:
            condition_staff = (Q(staff1=show_user)|Q(staff2=show_user)|Q(staff3=show_user)|Q(staff4=show_user)|\
                               Q(tr_staff1=show_user)|Q(tr_staff2=show_user)|Q(tr_staff3=show_user)|Q(tr_staff4=show_user))
        
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
        month_days  = calendar_context['month_days']
        month_first = month_days[0][0]
        month_last  = month_days[-1][-1]
        show_staff   = self.get_staff()

        calendar_context['month_day_schedules'] = self.get_month_schedules(
            month_first,
            month_last,
            month_days,
            show_staff,
        )
        return calendar_context