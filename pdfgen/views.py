from django.db.models.query_utils import Q
from schedules.models import Schedule
from careusers.models import CareUser
from django.http import HttpResponse,Http404
from django.views import View
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin,MonthWithScheduleMixin,jpweek
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black,white,dimgray,darkgray
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware,localtime
from django.db.models import Prefetch
import math

class PrintCalendarView(MonthWithScheduleMixin,View):
    model = Schedule

    def get(self,request, *args, **kwargs):

        filename = 'calendar' + '.pdf'
        #print(self.kwargs.get('year'))
        # pdf用のContent-TypeやContent-Dispositionをセット
        response = HttpResponse(status=200, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        # 即ダウンロードしたい時は、attachmentをつける
        # response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.filename)

        self._draw_main(response)
        return response

    def _draw_main(self, response):

        #スケジュールデータを取得
        calendar_data = self.get_month_data()

        #一日の最大スケジュール数を取得
        max=0
        for week_day_schedules in calendar_data['month_day_schedules']:
            for day, schedules in week_day_schedules.items():
                if self.kwargs.get('month') == day.month:
                    if len(schedules)>max:
                        max=len(schedules)

        #PDF描写
        #全体のカレンダー
        if calendar_data['staff_obj'] is None and calendar_data['careuser_obj'] is None:
            self._draw_all(response,calendar_data,max)
        #スタッフカレンダー
        elif calendar_data['staff_obj']:
            self._draw_staff(response,calendar_data,max)
        #利用者カレンダー
        elif calendar_data['careuser_obj']:
            self._draw_careuser(response,calendar_data,max)

    #スタッフごとのカレンダー
    def _draw_staff(self, response, calendar_data, max):

        # A4横書きのpdfを作る
        size = landscape(A4)
        title = '月間予定表'
        font = 'HeiseiMin-W3'
        is_bottomup = False
        # pdfを描く場所を作成：位置を決める原点は左上にする(bottomup)
        doc = canvas.Canvas(response, pagesize=size,bottomup=is_bottomup)
        # 日本語が使えるゴシック体のフォントを設定する
        pdfmetrics.registerFont(UnicodeCIDFont(font))
        # pdfのタイトルを設定
        doc.setTitle(title)

        #罫線描写////////////////////////////////////////////////////
        xlist = (30,142,254,365,478,590,702,812)

        #表示する週の数によって分岐
        if len(calendar_data['month_day_schedules']) <6:
            #5週Ver
            ylist = (40,55,158,261,364,467,570)
        else:
            #6週Ver
            ylist = (40,55,141,227,313,399,485,571)

        doc.grid(xlist, ylist)

        #タイトル////////////////////////////////////////////////////
        doc.setFont(font,14)
        title = str(self.kwargs.get('year')) + "年" + str(self.kwargs.get('month')) + "月　" + str(calendar_data['staff_obj']) + " 様　月間スケジュール"
        doc.drawString(280,30,title)
        #フォントサイズを戻す
        doc.setFont(font,10)
        now = make_aware(datetime.now())
        doc.drawString(680,35,now.strftime('%Y年%m月%d日%H時%M分出力'))

        #曜日////////////////////////////////////////////////////
        doc.drawString((xlist[1]+xlist[0])/2-5,52,"日")
        doc.drawString((xlist[2]+xlist[1])/2-5,52,"月")
        doc.drawString((xlist[3]+xlist[2])/2-5,52,"火")
        doc.drawString((xlist[4]+xlist[3])/2-5,52,"水")
        doc.drawString((xlist[5]+xlist[4])/2-5,52,"木")
        doc.drawString((xlist[6]+xlist[5])/2-5,52,"金")
        doc.drawString((xlist[7]+xlist[6])/2-5,52,"土")
        
        #データ////////////////////////////////////////////////////
        index_y = 0
        for week_day_schedules in calendar_data['month_day_schedules']:
            index_y +=1
            #print(ylist[index_y])
            index_x = -1
            for day, schedules in week_day_schedules.items():
                index_x +=1
                #日付表示////////////////////////////////////////////////////
                day_position_x = xlist[index_x]+3
                day_position_y = ylist[index_y]+12
                #日付文字
                if self.kwargs.get('month') != day.month:
                    day_text = str(day.month) + "/" + str(day.day)
                else:
                    day_text = str(day.day)

                #土日祝の背景色////////////////////////////////////////////////////
                if self.kwargs.get('month') == day.month:
                    if jpweek(day) =="祝" or jpweek(day) =="日":
                        doc.setFillColor("darkgrey")
                        if len(str(day.day))==1:
                            doc.rect(xlist[index_x]+1,ylist[index_y]+1,12,15,stroke=False,fill=True)
                        else:
                            doc.rect(xlist[index_x]+1,ylist[index_y]+1,16,15,stroke=False,fill=True)
                        doc.setFillColor("white")

                doc.setFont(font,12)
                #当月のみ表示 カレンダー上の前月末分は表示しない。
                if self.kwargs.get('month') == day.month:
                    doc.drawString(day_position_x,day_position_y,day_text)
                #文字色リセット
                doc.setFillColor("black")

                #スケジュール////////////////////////////////////////////////////
                sche_x = day_position_x+16
                sche_y = day_position_y
                doc.setFont(font,8)
                #当月のみ表示　カレンダー上の前月末分は表示しない。
                if self.kwargs.get('month') == day.month:
                    for schedule in schedules:
                        if schedule.report.careuser_confirmed:
                            sche_start = "実" + localtime(schedule.report.service_in_date).strftime("%H:%M")
                            sche_end   = localtime(schedule.report.service_out_date).strftime("%H:%M")
                        else:
                            sche_start = localtime(schedule.start_date).strftime("%H:%M")
                            sche_end   = localtime(schedule.end_date).strftime("%H:%M")
                        sche_user  = schedule.careuser.get_short_name()

                        if schedule.staff1 and schedule.staff1 != calendar_data['staff_obj']:sche_user += "[" + schedule.staff1.get_short_name() + "]"
                        if schedule.staff2 and schedule.staff2 != calendar_data['staff_obj']:sche_user += "[" + schedule.staff2.get_short_name() + "]"
                        if schedule.staff3 and schedule.staff3 != calendar_data['staff_obj']:sche_user += "[" + schedule.staff3.get_short_name() + "]"
                        if schedule.staff4 and schedule.staff4 != calendar_data['staff_obj']:sche_user += "[" + schedule.staff4.get_short_name() + "]"
                        if schedule.tr_staff1 and schedule.tr_staff1 != calendar_data['staff_obj']:sche_user += "[" + schedule.tr_staff1.get_short_name() + "]"
                        if schedule.tr_staff2 and schedule.tr_staff2 != calendar_data['staff_obj']:sche_user += "[" + schedule.tr_staff2.get_short_name() + "]"
                        if schedule.tr_staff3 and schedule.tr_staff3 != calendar_data['staff_obj']:sche_user += "[" + schedule.tr_staff3.get_short_name() + "]"
                        if schedule.tr_staff4 and schedule.tr_staff4 != calendar_data['staff_obj']:sche_user += "[" + schedule.tr_staff4.get_short_name() + "]"

                        sche_text  = str(sche_start) + "-" + str(sche_end) + " " + sche_user
                        doc.drawString(sche_x,sche_y,sche_text)
                        sche_y+=10
                #フォントサイズを戻す
                doc.setFont(font,10)
        doc.showPage()
        # pdfを保存
        doc.save()

    #全体カレンダー
    def _draw_all(self, response, calendar_data, max):

        # A4横書きのpdfを作る
        size = landscape(A4)
        pdf_title = '月間予定表'
        font = 'HeiseiMin-W3'
        is_bottomup = False
        # pdfを描く場所を作成：位置を決める原点は左上にする(bottomup)
        doc = canvas.Canvas(response, pagesize=size,bottomup=is_bottomup)
        # 日本語が使えるゴシック体のフォントを設定する
        pdfmetrics.registerFont(UnicodeCIDFont(font))

        page=0
        now = make_aware(datetime.now())

        for week_day_schedules in calendar_data['month_day_schedules']:
            index_y =1
            index_x = -1

            page +=1
            # pdfのタイトルを設定
            doc.setTitle(pdf_title)

            #罫線描写////////////////////////////////////////////////////
            xlist = (30,142,254,365,478,590,702,812)
            ylist = (40,55,571)
    
            doc.grid(xlist, ylist)

            #タイトル////////////////////////////////////////////////////
            doc.setFont(font,14)
            page_title = str(self.kwargs.get('year')) + "年" + str(self.kwargs.get('month')) + "月　全体スケジュール"
            page_title = page_title + " 第" + str(page) + "週目"
            doc.drawString(320,30,page_title)
            #フォントサイズを戻す
            doc.setFont(font,10)
            doc.drawString(680,35,now.strftime('%Y年%m月%d日%H時%M分出力'))

            #曜日////////////////////////////////////////////////////
            doc.drawString((xlist[1]+xlist[0])/2-5,52,"日")
            doc.drawString((xlist[2]+xlist[1])/2-5,52,"月")
            doc.drawString((xlist[3]+xlist[2])/2-5,52,"火")
            doc.drawString((xlist[4]+xlist[3])/2-5,52,"水")
            doc.drawString((xlist[5]+xlist[4])/2-5,52,"木")
            doc.drawString((xlist[6]+xlist[5])/2-5,52,"金")
            doc.drawString((xlist[7]+xlist[6])/2-5,52,"土")
            
            #データ////////////////////////////////////////////////////
            for day, schedules in week_day_schedules.items():
                index_x +=1
                #日付表示////////////////////////////////////////////////////
                day_position_x = xlist[index_x]+5
                day_position_y = ylist[index_y]+12
                #日付文字
                if self.kwargs.get('month') != day.month:
                    day_text = str(day.month) + "/" + str(day.day)
                else:
                    day_text = str(day.day)

                #土日祝の背景色////////////////////////////////////////////////////
                if self.kwargs.get('month') == day.month:
                    if jpweek(day) =="祝" or jpweek(day) =="日":
                        doc.setFillColor("darkgrey")
                        if len(str(day.day))==1:
                            doc.rect(xlist[index_x]+1,ylist[index_y]+1,15,15,stroke=False,fill=True)
                        else:
                            doc.rect(xlist[index_x]+1,ylist[index_y]+1,21,15,stroke=False,fill=True)

                        doc.setFillColor("white")

                doc.setFont(font,12)
                #当月のみ表示　カレンダー上の前月末分は表示しない。
                if self.kwargs.get('month') == day.month:
                    doc.drawString(day_position_x,day_position_y,day_text)
                #文字色リセット
                doc.setFillColor("black")

                #スケジュール////////////////////////////////////////////////////
                sche_x = day_position_x+5
                sche_y = day_position_y+12
                doc.setFont(font,8)
                #当月のみ表示　カレンダー上の前月末分は表示しない。
                if self.kwargs.get('month') == day.month:
                    for schedule in schedules:
                        if schedule.report.careuser_confirmed:
                            sche_start = "実" + localtime(schedule.report.service_in_date).strftime("%H:%M")
                            sche_end   = localtime(schedule.report.service_out_date).strftime("%H:%M")
                        else:
                            sche_start = localtime(schedule.start_date).strftime("%H:%M")
                            sche_end   = localtime(schedule.end_date).strftime("%H:%M")
                        sche_user  = schedule.careuser.get_short_name()
                        sche_staff = ""
                        if schedule.cancel_flg:
                            sche_staff += "Cancel"
                        else:
                            if(schedule.staff1):sche_staff += str(schedule.staff1.get_short_name())
                            if(schedule.staff2):sche_staff += " " + str(schedule.staff2.get_short_name())
                            if(schedule.staff3):sche_staff += " " + str(schedule.staff3.get_short_name())
                            if(schedule.staff4):sche_staff += " " + str(schedule.staff4.get_short_name())
                            if(schedule.tr_staff1):sche_staff += " " + str(schedule.tr_staff1.get_short_name())
                            if(schedule.tr_staff2):sche_staff += " " + str(schedule.tr_staff2.get_short_name())
                            if(schedule.tr_staff3):sche_staff += " " + str(schedule.tr_staff3.get_short_name())
                            if(schedule.tr_staff4):sche_staff += " " + str(schedule.tr_staff4.get_short_name())

                        sche_text  = str(sche_start) + "-" + str(sche_end) + "  " + sche_user + "  " +sche_staff
                        doc.drawString(sche_x,sche_y,sche_text)
                        sche_y+=10
                #フォントサイズを戻す
                doc.setFont(font,10)
            # Close the PDF object cleanly, and we're done.
            doc.showPage()
        # pdfを保存
        doc.save()

    #利用者カレンダー
    def _draw_careuser(self, response, calendar_data, max ):

        # A4横書きのpdfを作る
        size = landscape(A4)
        title = '月間予定表'
        font = 'HeiseiMin-W3'
        is_bottomup = False
        # pdfを描く場所を作成：位置を決める原点は左上にする(bottomup)
        doc = canvas.Canvas(response, pagesize=size,bottomup=is_bottomup)
        # 日本語が使えるゴシック体のフォントを設定する
        pdfmetrics.registerFont(UnicodeCIDFont(font))
        # pdfのタイトルを設定
        doc.setTitle(title)

        #罫線描写////////////////////////////////////////////////////
        xlist = (30,142,254,365,478,590,702,812)

        #表示する週の数によって分岐
        if len(calendar_data['month_day_schedules']) <6:
            #5週Ver
            ylist = (60,75,155,235,315,395,475)
        else:
            #6週Ver
            ylist = (60,75,145,215,285,355,425,495)

        doc.grid(xlist, ylist)

        #タイトル////////////////////////////////////////////////////
        doc.setFont(font,16)
        title = str(self.kwargs.get('year')) + "年" + str(self.kwargs.get('month')) + "月　" + str(calendar_data['careuser_obj']) + " 様　カレンダー"
        doc.drawString(280,50,title)
        #フォントサイズを戻す
        doc.setFont(font,10)
        now = make_aware(datetime.now())
        doc.drawString(680,55,now.strftime('%Y年%m月%d日%H時%M分出力'))


        #曜日////////////////////////////////////////////////////
        doc.drawString((xlist[1]+xlist[0])/2-5,72,"日")
        doc.drawString((xlist[2]+xlist[1])/2-5,72,"月")
        doc.drawString((xlist[3]+xlist[2])/2-5,72,"火")
        doc.drawString((xlist[4]+xlist[3])/2-5,72,"水")
        doc.drawString((xlist[5]+xlist[4])/2-5,72,"木")
        doc.drawString((xlist[6]+xlist[5])/2-5,72,"金")
        doc.drawString((xlist[7]+xlist[6])/2-5,72,"土")
        
        #データ////////////////////////////////////////////////////
        index_y = 0
        for week_day_schedules in calendar_data['month_day_schedules']:
            index_y +=1
            index_x = -1
            for day, schedules in week_day_schedules.items():
                index_x +=1
                #日付表示////////////////////////////////////////////////////
                day_position_x = xlist[index_x]+5
                day_position_y = ylist[index_y]+12
                #日付文字
                if self.kwargs.get('month') != day.month:
                    day_text = str(day.month) + "/" + str(day.day)
                else:
                    day_text = str(day.day)

                #土日祝の背景色////////////////////////////////////////////////////
                if self.kwargs.get('month') == day.month:
                    if jpweek(day) =="祝" or jpweek(day) =="日":
                        doc.setFillColor("darkgrey")
                        if len(str(day.day))==1:
                            doc.rect(xlist[index_x]+1,ylist[index_y]+1,15,15,stroke=False,fill=True)
                        else:
                            doc.rect(xlist[index_x]+1,ylist[index_y]+1,21,15,stroke=False,fill=True)
                        doc.setFillColor("white")

                doc.setFont(font,12)
                #当月のみ表示　カレンダー上の前月末分は表示しない。
                if self.kwargs.get('month') == day.month:
                    doc.drawString(day_position_x,day_position_y,day_text)
                #文字色リセット
                doc.setFillColor("black")

                #スケジュール////////////////////////////////////////////////////
                #当月のみ表示　カレンダー上の前月末分は表示しない。
                if self.kwargs.get('month') == day.month:
                    #スケジュールの最大数で分岐
                    if max>2:
                        sche_x = day_position_x+18
                        sche_y = day_position_y+3
                        doc.setFont(font,11)
                        for schedule in schedules:
                            if schedule.cancel_flg is False:
                                sche_staff = ""
                                peoples = schedule.peoples

                                if schedule.staff1:sche_staff += str(schedule.staff1.get_short_name())
                                if schedule.staff2:sche_staff += "・" + str(schedule.staff2.get_short_name())
                                if schedule.staff3:sche_staff += "・" + str(schedule.staff3.get_short_name())
                                if schedule.staff4:sche_staff += "・" + str(schedule.staff4.get_short_name())
                                
                                if schedule.tr_staff1:
                                    if schedule.staff1:sche_staff += "・"
                                    sche_staff += str(schedule.tr_staff1.get_short_name())
                                    peoples += 1
                                if schedule.tr_staff2:
                                    sche_staff += "・" + str(schedule.tr_staff2.get_short_name())
                                    peoples += 1
                                if schedule.tr_staff3:
                                    sche_staff += "・" + str(schedule.tr_staff3.get_short_name())
                                    peoples += 1
                                if schedule.tr_staff4:
                                    sche_staff += "・" + str(schedule.tr_staff4.get_short_name())
                                    peoples += 1

                                if schedule.report.careuser_confirmed:
                                    sche_start = localtime(schedule.report.service_in_date).strftime("%H:%M")
                                    sche_end   = localtime(schedule.report.service_out_date).strftime("%H:%M")
                                else:
                                    sche_start = localtime(schedule.start_date).strftime("%H:%M")
                                    sche_end   = localtime(schedule.end_date).strftime("%H:%M")

                                if peoples>1:
                                    sche_text  = str(sche_start) + "-" + str(sche_end)
                                    doc.drawString(sche_x,sche_y,sche_text)
                                    name_x=sche_x+5
                                    sche_y+=11
                                    sche_text  = sche_staff
                                    doc.drawString(name_x,sche_y,sche_text)
                                    sche_y+=13
                                elif len(sche_staff)>2:
                                    text0_2 = sche_staff[0:2]
                                    sche_text  = str(sche_start) + "-" + str(sche_end) + "  " + str(text0_2)
                                    doc.drawString(sche_x,sche_y,sche_text)
                                    name_x=sche_x+60
                                    sche_y+=11
                                    sche_text  = sche_staff[2:]
                                    doc.drawString(name_x,sche_y,sche_text)
                                    sche_y+=13
                                else:
                                    sche_text  = str(sche_start) + "-" + str(sche_end) + "  " + sche_staff
                                    doc.drawString(sche_x,sche_y,sche_text)
                                    sche_y+=13

                    else:
                        sche_x = day_position_x+25
                        sche_y = day_position_y+3
                        doc.setFont(font,16)
                        for schedule in schedules:
                            if schedule.cancel_flg is False:
                                sche_staff = ""
                                peoples = schedule.peoples

                                if schedule.staff1:sche_staff += str(schedule.staff1.get_short_name())
                                if schedule.staff2:sche_staff += "・" + str(schedule.staff2.get_short_name())
                                if schedule.staff3:sche_staff += "・" + str(schedule.staff3.get_short_name())
                                if schedule.staff4:sche_staff += "・" + str(schedule.staff4.get_short_name())
                                
                                if schedule.tr_staff1:
                                    if schedule.staff1:sche_staff += "・"
                                    sche_staff += str(schedule.tr_staff1.get_short_name())
                                    peoples += 1
                                if schedule.tr_staff2:
                                    sche_staff += "・" + str(schedule.tr_staff2.get_short_name())
                                    peoples += 1
                                if schedule.tr_staff3:
                                    sche_staff += "・" + str(schedule.tr_staff3.get_short_name())
                                    peoples += 1
                                if schedule.tr_staff4:
                                    sche_staff += "・" + str(schedule.tr_staff4.get_short_name())
                                    peoples += 1

                                if schedule.report.careuser_confirmed:
                                    sche_start = localtime(schedule.report.service_in_date).strftime("%H:%M")
                                    sche_end   = localtime(schedule.report.service_out_date).strftime("%H:%M")
                                else:
                                    sche_start = localtime(schedule.start_date).strftime("%H:%M")
                                    sche_end   = localtime(schedule.end_date).strftime("%H:%M")
                                sche_text  = str(sche_start) + "-" + str(sche_end)
                                doc.drawString(sche_x,sche_y,sche_text)

                                name_x=sche_x-18
                                sche_y+=17

                                #半角を全角換算して文字を数える
                                str_cnt = len_fullwidth(sche_staff)

                                if str_cnt<6:
                                    add_sp =""
                                    for i in range(6-str_cnt):
                                        add_sp += "　"

                                    sche_staff = add_sp + sche_staff
                                
                                doc.drawString(name_x,sche_y,sche_staff)
                                sche_y+=17
                                

                #フォントサイズを戻す
                doc.setFont(font,11)

                #備考・会社名
                biko_x = 140
                biko_y = ylist[-1]+20
                doc.setFont(font,15)
                doc.drawString(biko_x,biko_y,"※業務上の都合により、連絡なく変更する場合がございます。予めご了承下さい。")
                biko_x = 270
                biko_y += 28
                doc.setFont(font,18)
                doc.drawString(biko_x,biko_y,"介護ステーションはな　072-744-3410")
        # Close the PDF object cleanly, and we're done.
        doc.showPage()
        # pdfを保存
        doc.save()


class PrintMonthlyReportView(StaffUserRequiredMixin,View):
    model = Schedule

    def get(self,request, *args, **kwargs):

        filename = "monthly_report" + '.pdf'
        #print(self.kwargs.get('year'))
        # pdf用のContent-TypeやContent-Dispositionをセット
        response = HttpResponse(status=200, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        # 即ダウンロードしたい時は、attachmentをつける
        # response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.filename)

        self._draw_main(response)
        return response

    def _draw_main(self, response):

        self.year = self.kwargs.get('year')
        self.month= self.kwargs.get('month')

        this_month   = datetime(self.year,self.month,1)
        this_month   = make_aware(this_month)
        next_month   = this_month + relativedelta(months=1)

        condition_careuser = Q()
        if self.request.GET.get('careuser'):
            condition_careuser = Q(careuser=CareUser(pk=self.request.GET.get('careuser')))
        #キャンセルでなく、reportの利用者確認（記録の入力）がされたもののみを抽出
        queryset = self.model.objects.select_related('report','careuser','service','staff1','staff2','staff3','staff4','tr_staff1','tr_staff2','tr_staff3','tr_staff4').filter(condition_careuser,start_date__range=[this_month,next_month],cancel_flg=False,report__careuser_confirmed=True)

        #PDF描写
        if queryset.count():
            self._draw_monthly_report(response,queryset)
        else:
            raise Http404

    #月間サービス実施記録
    def _draw_monthly_report(self, response, sche_data):

        # A4縦書きのpdfを作る
        title = str(self.year) + "年" + str(self.month) + "月度　サービス実施記録"
        is_bottomup = False
        # pdfを描く場所を作成：位置を決める原点は左上にする(bottomup)
        doc = canvas.Canvas(response,bottomup=is_bottomup)
        # pdfのタイトルを設定
        doc.setTitle(title)

        #利用者を抽出
        dist_care_users = sche_data.all().values_list('careuser').distinct().order_by('careuser__last_kana','careuser__first_kana')

        for careuser_tuple in dist_care_users:

            #使用したサービスカテゴリで分類
            dist_used_kind = sche_data.filter(careuser=careuser_tuple[0]).values_list('service__kind').distinct().order_by('service__kind')

            for kind_tuple in dist_used_kind:
                if kind_tuple[0] == 0:
                    #介護保険のリストを作成
                    self.drow_report(doc,sche_data,careuser_tuple[0],kind_tuple[0])
                elif kind_tuple[0] == 1:
                    #障害者総合支援のリストを作成
                    self.drow_report(doc,sche_data,careuser_tuple[0],kind_tuple[0])
                elif kind_tuple[0] == 2:
                    #移動支援のリストを作成
                    self.drow_report(doc,sche_data,careuser_tuple[0],kind_tuple[0])
                elif kind_tuple[0] == 3:
                    #総合事業のリストを作成
                    self.drow_report(doc,sche_data,careuser_tuple[0],kind_tuple[0])
                elif kind_tuple[0] == 4:
                    #同行援護のリストを作成
                    self.drow_report(doc,sche_data,careuser_tuple[0],kind_tuple[0])
                elif kind_tuple[0] == 5:
                    #自費のリストを作成
                    self.drow_report(doc,sche_data,careuser_tuple[0],kind_tuple[0])
        
        #pdfを保存
        doc.save()

    def drow_report(self,doc,sche_data,careuser_key,kind_key):
    
        sche_by_careuser = sche_data.filter(careuser__pk=careuser_key,service__kind=kind_key).order_by('report__service_in_date')

        if  sche_by_careuser:
            

            # 日本語が使えるフォントを設定する
            font = 'HeiseiMin-W3'
            pdfmetrics.registerFont(UnicodeCIDFont(font))
           
            #罫線（セル）の設定
            xlist = [30,83,110,150,174,234,336,388,570]
            colum_title = ['実施日時','','サービス名','ヘルパー','実施内容']
            pre_check_title   ='[事　前チェック] '
            physical_title    ='[身　体　介　護] '
            life_title        ='[生　活　援　助] '
            after_check_title ='[退　室　確　認] '
            biko_title        ='[特記・連絡事項] '
            #セル開始位置
            y_start = 60
            y_end =800
            #ヘッダー開始位置
            x_head = 40
            y_head = 50
            header_fontsize = 16
            #カラム
            colum_fontsize = 10
            #行間
            y_margin = 10          
            #フッダー開始位置
            x_foot = 400
            y_foot = 810
            footer_fontsize = 16
            #ページ枚数記載位置
            x_page = 290
            y_page = 812
            page_fontsize = 12

            #一件当たりのセルサイズ//////////////////////////
            x_width = 540
            val_fontsize = 10
            #実施日時・サービス・担当者の行の高さ
            row_title_height =20
            #実施内容欄
            content_fontsize = 8
            #一行に割り当てる高さ
            row_height= 16
            #左側タイトルを除くmax文字数
            row_max_text=59
            biko_max_text=50

            #設定ここまで/////////////////////////////////////////

            #実施内容欄の行数を確認するため、テキストデータをここで作成
            rows_text = self.get_text_data(sche_by_careuser,row_max_text,biko_max_text)
            y_height    = []#一件ごとの行のトータル
            in_y_height = []#一件ごとの実施内容欄の高さ
            
            total_pages = 1
            h_point = y_start
            ylist = []#一件毎のスタートy座標

            for index,row in enumerate(rows_text):

                in_y_height.insert(index,[row_title_height,row_height*row['total_rows']]) #セル内上下分割
                y_height.insert(index,in_y_height[index][0]+in_y_height[index][1])

                row_end =  h_point + y_height[index]
                if row_end >y_end:
                    total_pages +=1 #総ページ数
                    h_point = y_start
                    ylist.insert(index,h_point)
                    h_point += y_height[index]+y_margin
                else:
                    ylist.insert(index,h_point)
                    h_point += y_height[index]+y_margin
            
            current_page = 0

            for index,txt in enumerate(rows_text):
                #上記設定にて描写
                #ヘッダー・フッター//////////////////////////////////////////////////////////////
                if ylist[index] == y_start:
                    current_page+=1
                    #罫線描写
                    #doc.grid(xlist, ylist)
                    
                    #ヘッダータイトル
                    doc.setFont(font,header_fontsize)
                    doc.drawString(x_head,y_head,txt['head_txt'])
                    #ページ
                    doc.setFont(font,page_fontsize)
                    doc.drawString(x_page,y_page,str(current_page) +' / ' + str(total_pages))
                    #フッター
                    doc.setFont(font,footer_fontsize)
                    doc.drawString(x_foot,y_foot,txt['foot_txt'])

                #外枠の描写
                doc.setStrokeColor(dimgray)
                doc.setLineWidth(2)
                doc.rect(xlist[0] ,ylist[index] ,x_width ,y_height[index])
                doc.setLineWidth(0.5)
                
                #カラム名フォントサイズ
                doc.setFont(font,colum_fontsize)
                #行描写
                #日付
                #タイトル中央
                doc.setFillColor(dimgray)
                doc.rect(xlist[0],ylist[index],xlist[1]-xlist[0],in_y_height[index][0],fill=True)
                
                doc.setFillColor(white)
                doc.drawString((xlist[0]+xlist[1]-len_halfwidth(colum_title[0])*val_fontsize/2)/2,(ylist[index]*2+in_y_height[index][0]+val_fontsize-2)/2,colum_title[0])
                doc.setFillColor(black)
                
                #日付　右詰め
                doc.drawString(xlist[2]-len_halfwidth(txt['day'])*colum_fontsize/2,(ylist[index]*2+in_y_height[index][0]+val_fontsize-2)/2,txt['day'])
                #時間
                doc.drawString(xlist[2]+2,(ylist[index]*2+in_y_height[index][0]+val_fontsize-2)/2,txt['time'])
                
                #サービス名称
                #タイトル中央
                doc.setFillColor(dimgray)
                doc.rect(xlist[4],ylist[index],xlist[5]-xlist[4],in_y_height[index][0],fill=True)
                doc.setFillColor(white)
                doc.drawString((xlist[4]+xlist[5]-len_halfwidth(colum_title[2])*val_fontsize/2)/2,(ylist[index]*2+in_y_height[index][0]+val_fontsize-2)/2,colum_title[2])
                doc.setFillColor(black)
                doc.drawString(xlist[5]+3,(ylist[index]*2+in_y_height[index][0]+val_fontsize-2)/2,txt['service'])
                
                #担当ヘルパー
                #タイトル中央
                doc.setFillColor(dimgray)
                doc.rect(xlist[6],ylist[index],xlist[7]-xlist[6],in_y_height[index][0],fill=True)
                doc.setFillColor(white)
                doc.drawString((xlist[6]+xlist[7]-len_halfwidth(colum_title[3])*val_fontsize/2)/2,(ylist[index]*2+in_y_height[index][0]+val_fontsize-2)/2,colum_title[3])
                doc.setFillColor(black)
                doc.drawString(xlist[7]+3,(ylist[index]*2+in_y_height[index][0]+val_fontsize-2)/2,txt['helpers'])
                #実施内容
                #タイトル中央
                doc.setFillColor(dimgray)
                doc.rect(xlist[0],ylist[index]+in_y_height[index][0],xlist[1]-xlist[0],in_y_height[index][1],fill=True)
                doc.setFillColor(white)
                doc.drawString((xlist[0]+xlist[1]-len_halfwidth(colum_title[4])*val_fontsize/2)/2,((ylist[index]+in_y_height[index][0])*2+in_y_height[index][1]+val_fontsize-2)/2,colum_title[4])
                doc.setFillColor(black)
                doc.setFont(font,content_fontsize)
                
                cnt=0;
                if txt['pre_check']:
                    doc.drawString(xlist[1]+3,ylist[index]+in_y_height[index][0]+row_height*(cnt+1)-(row_height-content_fontsize+3)/2,pre_check_title)
                    doc.drawString(xlist[3]+3,ylist[index]+in_y_height[index][0]+row_height*(cnt+1)-(row_height-content_fontsize+3)/2,txt['pre_check'][0])
                cnt += len(txt['pre_check'])

                if txt['physical']:
                    doc.drawString(xlist[1]+3,ylist[index]+in_y_height[index][0]+row_height*(cnt+1)-(row_height-content_fontsize+3)/2,physical_title)
                    for i,row_txt in enumerate(txt['physical']):
                        doc.drawString(xlist[3]+3,ylist[index]+in_y_height[index][0]+row_height*(cnt+i+1)-(row_height-content_fontsize+3)/2,txt['physical'][i])
                cnt += len(txt['physical'])

                if txt['life']:
                    doc.drawString(xlist[1]+3,ylist[index]+in_y_height[index][0]+row_height*(cnt+1)-(row_height-content_fontsize+3)/2,life_title)
                    for i,row_txt in enumerate(txt['life']):
                        doc.drawString(xlist[3]+3,ylist[index]+in_y_height[index][0]+row_height*(cnt+i+1)-(row_height-content_fontsize+3)/2,txt['life'][i])
                cnt += len(txt['life'])

                if txt['after_check']:
                    doc.drawString(xlist[1]+3,ylist[index]+in_y_height[index][0]+row_height*(cnt+1)-(row_height-content_fontsize+3)/2,after_check_title)
                    doc.drawString(xlist[3]+3,ylist[index]+in_y_height[index][0]+row_height*(cnt+1)-(row_height-content_fontsize+3)/2,txt['after_check'][0])
                cnt += len(txt['after_check'])

                if txt['biko']:
                    doc.drawString(xlist[1]+3,ylist[index]+in_y_height[index][0]+row_height*(cnt+1)-(row_height-content_fontsize+3)/2,biko_title)
                    for i,row_txt in enumerate(txt['biko']):
                        doc.drawString(xlist[3]+3,ylist[index]+in_y_height[index][0]+row_height*(cnt+i+1)-(row_height-content_fontsize+3)/2,txt['biko'][i])
                cnt += len(txt['biko'])

                #中央線を追加
                doc.setStrokeColor(darkgray)
                doc.setLineWidth(0.5)
                doc.line(xlist[0] ,ylist[index]+in_y_height[index][0] ,xlist[0]+x_width,ylist[index]+in_y_height[index][0])
                doc.setStrokeColor(dimgray)
                
                #改ページ 
                if index == len(rows_text)-1 or ylist[index+1] == y_start :
                    doc.showPage()
            
        

    def get_text_data(self,sche_by_careuser,row_max_text,biko_max_text):
        from schedules.views import report_for_output
        kind_dict = {0:'介護保険',1:'障害者総合支援',2:'移動支援',3:'総合事業',4:'同行援護',5:'自費'}
        
        ret_repords=[]

        for sche in sche_by_careuser:
            output_data ={}
            #設定/////////////////////////////////////////////////////////////////////////////////////////
            service_in_date  = localtime(sche.report.service_in_date)
            service_out_date = localtime(sche.report.service_out_date)
            output_data['head_txt'] = str(sche_by_careuser[0].careuser) + " 様　　" + str(service_in_date.year) + "年" + str(service_in_date.month) + "月度　" +  kind_dict[sche.service.kind] + "サービス実施記録"
            output_data['foot_txt'] = '介護ステーションはな'
            
            
            service_in_date_time = service_in_date.strftime("%H").lstrip("0") + ":" + service_in_date.strftime("%M")
            service_out_date_time   = service_out_date.strftime("%H").lstrip("0") + ":" + service_out_date.strftime("%M")
            output_data['day'] = str(service_in_date.day) + "日"
            output_data['time'] =  service_in_date_time + "～" + service_out_date_time

            output_data['service'] = sche.service.user_title

            repo = report_for_output(sche.report)
            report = []
            #ヘルパー
            helpers = ""
            if repo['conf']['staffs']:
                for staff in repo['conf']['staffs']:
                    if helpers == "":
                        helpers += staff
                    else:
                        helpers += "  " + staff
            if repo['conf']['tr_staffs']:
                helpers += "  [同行]"
                for staff in repo['conf']['tr_staffs']:
                    helpers += "  " + staff

            output_data['helpers'] = helpers

            #事前チェック
            pre_check_list = []
            if repo['pre_check']:
                pre_check= ""
                for checked in repo['pre_check']:
                    if pre_check == "":
                        pre_check += checked
                    else:
                        pre_check += " " +checked
                #文字数がrow_max_textを超えることはない。
                pre_check_list.append(pre_check)
            output_data['pre_check'] = pre_check_list

            #身体
            physical_list = []
            if repo['physical']:
                physical = ""
                add_row_text = ""
                for genre,services in repo['physical'].items():
                    if  physical == "":
                        add_row_text += "<" + genre + ">"
                    else:
                        add_row_text += " <" + genre + ">"
                    firstloop = True
                    for checked in services:
                        if firstloop:
                            add_row_text += checked
                            firstloop = False
                        else:
                            add_row_text += " " +checked

                        #文字数がオーバーしなければ追加
                        len_phy = len(physical)
                        len_add = len(add_row_text)
                        if (len_phy + len_add ) <= row_max_text:
                            physical += add_row_text
                        #オーバーする場合は新たなリストを作成し追加。
                        else:
                            #単独で行数オーバーの場合
                            if len_add >=row_max_text:
                                #一旦今の内容を書き込み、新たな行から分割してlist追加
                                physical_list.append(physical);
                                physical = ""
                                add_list = [add_row_text[i:i+row_max_text] for i in range(0,len(add_row_text), row_max_text)]
                                for a in add_list:
                                    if len(a)>=row_max_text:
                                        physical_list.append(a)
                                #最終行の文字数を取得 
                                if(len(add_list[-1]) < row_max_text-8):
                                    #8文字以上余裕あれば追加せず次回に回す。
                                    physical +=  add_list[-1]
                                else:
                                    physical_list.append(add_list[-1])
                                    physical = ""
                            else:
                                #続けて記載し分割して登録する。
                                physical += add_row_text
                                add_list = [physical[i:i+row_max_text] for i in range(0,len(physical), row_max_text)]

                                for a in add_list:
                                     if len(a)>=row_max_text:
                                        physical_list.append(a)
                                        physical = ""
                                #最終行の文字数を取得 
                                if(len(add_list[-1]) < row_max_text-8):
                                    #8文字以上余裕あれば追加せず次回に回す。
                                    physical +=  add_list[-1]
                                else:
                                    physical_list.append(add_list[-1])
                                    physical = ""
                        #初期化
                        add_row_text=""
                physical_list.append(physical)
            output_data['physical'] = physical_list

            #生活
            life_list = []
            if repo['life']:
                life = ""
                add_row_text = ""
                for genre,services in repo['life'].items():
                    if  life == "":
                        add_row_text += "<" + genre + ">"
                    else:
                        add_row_text += " <" + genre + ">"
                    firstloop = True
                    for checked in services:
                        if firstloop:
                            add_row_text += checked
                            firstloop = False
                        else:
                            add_row_text += " " +checked

                        #文字数がオーバーしなければ追加
                        if len(life + add_row_text) <= row_max_text:
                            life +=  add_row_text
                        #オーバーする場合は新たなリストを作成し追加。
                        else:
                            #現在の文字数でリストに登録
                            life_list.append(life)
                            #初期化して追加
                            life = "" + add_row_text
                        #初期化
                        add_row_text=""
                life_list.append(life)
            output_data['life'] = life_list

            #退室確認
            after_check_list = []
            if repo['after_check']:
                after_check = ""
                for checked in repo['after_check']:
                    if after_check == "":
                        after_check += checked
                    else:
                        after_check += " " +checked
                #文字数がrow_max_textを超えることはない。
                after_check_list.append(after_check)
            output_data['after_check'] = after_check_list

            #特記・連絡事項  行先についても特記事項に追記する
            biko_list = []
            if repo['biko']:
                biko = ""
                if repo['destination']:
                    biko = repo['destination'] + '　' + repo['biko']
                else:
                    biko = repo['biko']

                #全角スペースを半角に置換
                biko = biko.replace('　',' ')
                biko = biko.replace('\n','').replace('\r','')

                #文字を分割してリストに格納
                biko_list = [biko[i:i+biko_max_text] for i in range(0,len(biko), biko_max_text)]
            output_data['biko'] = biko_list
            
            #全行数を計算
            output_data['total_rows'] = len(pre_check_list)+len(physical_list)+len(life_list)+len(after_check_list)+len(biko_list)

            ret_repords.append(output_data)

        return ret_repords



class PrintVisitedListFormView(StaffUserRequiredMixin,View):
    model = CareUser

    def get(self,request, *args, **kwargs):

        filename = 'visitedform' + '.pdf'
        #print(self.kwargs.get('year'))
        # pdf用のContent-TypeやContent-Dispositionをセット
        response = HttpResponse(status=200, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        # 即ダウンロードしたい時は、attachmentをつける
        # response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.filename)

        self._draw_main(response)
        return response

    def _draw_main(self, response):

        self.year     = self.kwargs.get('year')
        self.month    = self.kwargs.get('month')

        this_month   = datetime(self.year,self.month,1)
        this_month   = make_aware(this_month)
        next_month   = this_month + relativedelta(months=1)

        condition_careuser = Q()
        if self.request.GET.get('careuser'):
            condition_careuser = Q(pk=self.request.GET.get('careuser'))

        #アクティブな利用者と紐づく月間スケジュールをすべて取得 to_attrを用いて、多次元リストで取得
        careusers_data = self.model.objects.prefetch_related(Prefetch("schedule_set",queryset=Schedule.objects.select_related('service').filter(start_date__range=[this_month,next_month],cancel_flg=False).order_by('start_date'),to_attr="sche")).filter(condition_careuser,is_active=True,).order_by('-is_active','last_kana','first_kana')
        self._draw_visitform(response,careusers_data)

    #月間サービス実施記録
    def _draw_visitform(self, response, careusers_data):

        # A4縦書きのpdfを作る
        title = str(self.year) + "年" + str(self.month) + "月度　訪問記録票"
        is_bottomup = False
        # pdfを描く場所を作成：位置を決める原点は左上にする(bottomup)
        doc = canvas.Canvas(response,bottomup=is_bottomup)
        # pdfのタイトルを設定
        doc.setTitle(title)
       
        #利用者を抽出
        for c_u_listdata in careusers_data:
            #querysetにフィルターを掛けると新たにクエリが実行されるため、上記でto_attrを用いて、多次元リストで取得
            #サービスの重複を除いたリストを作成
            kind_list = []
            sche_listobj_by_kind={}
            for sche in c_u_listdata.sche:
                if sche.service.kind not in kind_list:
                    kind_list.append(sche.service.kind)
                    #sche辞書内にkind毎に分類するリストを作成
                    sche_listobj_by_kind[sche.service.kind]=[]
                #リストスケジュールをフィルターして分割する
                sche_listobj_by_kind[sche.service.kind].append(sche)

            kind_list.sort()

            for kind_key in kind_list:
                if kind_key == 0:
                    #介護保険のリストを作成
                    self.drow_visitedlist(doc,sche_listobj_by_kind[kind_key],kind_key)
                #elif kind_key == 1:
                    #障害者総合支援のリストを作成
                #    self.drow_visitedlist(doc,sche_listobj_by_kind[kind_key],kind_key)
                #elif kind_key == 2:
                    #移動支援のリストを作成
                #    self.drow_visitedlist(doc,sche_listobj_by_kind[kind_key],kind_key)
                elif kind_key == 3:
                    #総合事業のリストを作成
                    self.drow_visitedlist(doc,sche_listobj_by_kind[kind_key],kind_key)
                elif kind_key == 4:
                    #同行援護のリストを作成
                    self.drow_visitedlist(doc,sche_listobj_by_kind[kind_key],kind_key)
                elif kind_key == 5:
                    #自費のリストを作成
                    self.drow_visitedlist(doc,sche_listobj_by_kind[kind_key],kind_key)

        #pdfを保存
        doc.save()    

    def drow_visitedlist(self,doc,sche_by_kind,kind_key):
        
        kind_dict = {0:'介護保険',1:'障害者総合支援',2:'移動支援',3:'総合事業',4:'同行援護',5:'自費'}

        # 日本語が使えるフォントを設定する
        font = 'HeiseiMin-W3'
        pdfmetrics.registerFont(UnicodeCIDFont(font))
        
        #罫線（セル）の設定
        xlist = [30,70,220,370,510,560]
        #セル開始位置
        y_start = 90
        #行間
        y_height = 30
        #ヘッダー開始位置
        x_head = 40
        y_head = 50
        header_fontsize = 16
        #上部テキスト
        x_top_txt = 34
        y_top_txt = 80
        top_txt_fontsize =11
        #カラム名
        colum_height = 25
        colum_fontsize = 10
        colum_title = ["日","時間","サービス名称","担当ヘルパー","利用者印"]
        #行
        val_fontsize = 10
        #フッダー開始位置
        x_foot = 400
        y_foot = 800
        footer_fontsize = 16
        #ページ枚数記載位置
        x_page = 290
        y_page = 812
        page_fontsize = 12

        #設定ここまで/////////////////////////////////////////
        ylist = [y_start]
        y_add = y_start + colum_height
        #記載可能行数を取得
        sche_cnt_in_page=-1
        #ylist作成
        while y_add < 800:
            ylist.append(y_add)
            y_add +=y_height
            sche_cnt_in_page+=1

        #総ページ数
        total_pages = math.ceil(len(sche_by_kind)/sche_cnt_in_page)
        current_page = 0

        for index in range(sche_cnt_in_page*total_pages):
            #設定/////////////////////////////////////////////////////////////////////////////////////////
            
            head_txt = str(sche_by_kind[0]) + " 様　　" + str(self.year) + "年" + str(self.month) + "月度　" +  kind_dict[kind_key] + "訪問記録"
            top_txt  = "サービス実施記録につきましてはデータにて保管しており、翌月初旬に書面にてお届け致します。"
            foot_txt = '介護ステーションはな'
            time = "　　：　　～　　：　　"
            sign = "印"
            val_list=["",time,"","",sign]

            #上記設定にて描写
            #ヘッダー・フッター//////////////////////////////////////////////////////////////
            if index==0 or (index+1)%sche_cnt_in_page==1:
                current_page+=1
                #罫線
                doc.grid(xlist, ylist)
                #ヘッダータイトル
                doc.setFont(font,header_fontsize)
                doc.drawString(x_head,y_head,head_txt)
                #利用者名アンダーライン
                #doc.setLineWidth(1.2)
                #doc.line(x_head-10,y_head+7,x_head+125,y_head+7)
                #topテキスト
                doc.setFont(font,top_txt_fontsize)
                doc.drawString(x_top_txt,y_top_txt,top_txt)
                #ページ
                #doc.setFont(font,page_fontsize)
                #doc.drawString(x_page,y_page,str(current_page) +' / ' + str(total_pages))
                #フッター
                doc.setFont(font,footer_fontsize)
                doc.drawString(x_foot,y_foot,foot_txt)
                #カラム名フォントサイズ
                doc.setFont(font,colum_fontsize)
                #カラム描写　セルの座標合計から文字数*fontsizeを引く
                for i,colum in enumerate(colum_title):
                    doc.drawString((xlist[i]+xlist[i+1]-len_halfwidth(colum)*colum_fontsize/2)/2,(y_start*2+colum_height+colum_fontsize)/2,colum)
                
            #行描写セルの座標合計から文字数*fontsize(半角は半分)を引く
            for i,val in enumerate(val_list):
                if val:
                    doc.drawString((xlist[i]+xlist[i+1]-len_halfwidth(val)*val_fontsize/2)/2,(ylist[(index%sche_cnt_in_page)+1]+ylist[(index%(sche_cnt_in_page))+2]+val_fontsize)/2,val)
            #改ページ 
            if index == sche_cnt_in_page*total_pages-1 or (index+1)%sche_cnt_in_page==0 :
                doc.showPage()


    def drow_list(self,doc,sche_by_kind,kind_key):
        
        kind_dict = {0:'介護保険',1:'障害者総合支援',2:'移動支援',3:'総合事業',4:'同行援護',5:'自費'}

        # 日本語が使えるフォントを設定する
        font = 'HeiseiMin-W3'
        pdfmetrics.registerFont(UnicodeCIDFont(font))
        
        #罫線（セル）の設定
        xlist = [30,60,140,220,300,570]
        #セル開始位置
        y_start = 60
        #行間
        y_height = 40

        #ヘッダー開始位置
        x_head = 40
        y_head = 50
        header_fontsize = 16
        #カラム名
        colum_height = 25
        colum_fontsize = 10
        colum_title = ["日","時間","サービス名称","担当ヘルパー","実施記録"]
        #行
        val_fontsize = 10
        #フッダー開始位置
        x_foot = 400
        y_foot = 805
        footer_fontsize = 16
        #ページ枚数記載位置
        x_page = 290
        y_page = 812
        page_fontsize = 12

        #設定ここまで/////////////////////////////////////////
        ylist = [y_start]
        y_add = y_start + colum_height
        #記載可能行数を取得
        sche_cnt_in_page=-1
        #ylist作成
        while y_add < 800:
            ylist.append(y_add)
            y_add +=y_height
            sche_cnt_in_page+=1

        #総ページ数
        total_pages = math.ceil(len(sche_by_kind)/sche_cnt_in_page)
        current_page = 0

        for index,sche in enumerate(sche_by_kind):
            #設定/////////////////////////////////////////////////////////////////////////////////////////
            start = localtime(sche.start_date)
            end   = localtime(sche.end_date)

            head_txt = str(sche) + " 様　　" + str(self.year) + "年" + str(self.month) + "月度　" +  kind_dict[kind_key] + "訪問記録"
            foot_txt = '介護ステーションはな'
            
            day = str(start.day)

            start_time = start.strftime("%H").lstrip("0") + ":" + start.strftime("%M")
            end_time   = end.strftime("%H").lstrip("0") + ":" + end.strftime("%M")
            write_time =  start_time + "～" + end_time

            service_name = sche.service.user_title

            helpers = ""

            val_list=[day,write_time,service_name,helpers]

            #上記設定にて描写
            #ヘッダー・フッター//////////////////////////////////////////////////////////////
            if index==0 or (index+1)%sche_cnt_in_page==1:
                current_page+=1
                #罫線
                doc.grid(xlist, ylist)
                #ヘッダータイトル
                doc.setFont(font,header_fontsize)
                doc.drawString(x_head,y_head,head_txt)
                #ページ
                doc.setFont(font,page_fontsize)
                doc.drawString(x_page,y_page,str(current_page) +' / ' + str(total_pages))
                #フッター
                doc.setFont(font,footer_fontsize)
                doc.drawString(x_foot,y_foot,foot_txt)
                #カラム名フォントサイズ
                doc.setFont(font,colum_fontsize)
                #カラム描写　セルの座標合計から文字数*fontsizeを引く
                for i,colum in enumerate(colum_title):
                    doc.drawString((xlist[i]+xlist[i+1]-len_halfwidth(colum)*colum_fontsize/2)/2,(y_start*2+colum_height+colum_fontsize)/2,colum)
                
            #行描写セルの座標合計から文字数*fontsize(半角は半分)を引く
            for i,val in enumerate(val_list):
                doc.drawString((xlist[i]+xlist[i+1]-len_halfwidth(val)*val_fontsize/2)/2,(ylist[(index%sche_cnt_in_page)+1]+ylist[(index%(sche_cnt_in_page))+2]+val_fontsize)/2,val)
            #改ページ 
            if index == len(sche_by_kind)-1 or (index+1)%sche_cnt_in_page==0 :
                doc.showPage()
        

def len_fullwidth(text):
    import unicodedata as uni
    import math
    #半角文字を全角換算して文字数を返す
    return math.floor(sum([(0.5, 1)[uni.east_asian_width(t) in 'FWA'] for t in text]))

def len_halfwidth(text):
    import unicodedata as uni
    import math
    #半角文字を全角換算して文字数を返す
    return math.floor(sum([(1, 2)[uni.east_asian_width(t) in 'FWA'] for t in text]))