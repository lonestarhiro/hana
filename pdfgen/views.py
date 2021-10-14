from django.db.models.query_utils import Q
from schedules.models import Schedule
from django.http import HttpResponse
from django.views import View
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin,MonthWithScheduleMixin
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from django.utils.timezone import make_aware,localtime

#以下staffuserのみ表示（下のStaffUserRequiredMixinにて制限中）
class CalendarView(StaffUserRequiredMixin,MonthWithScheduleMixin,View):
    model = Schedule
    order_date_field = "start_date"


    def get(self,request, *args, **kwargs):

        filename = str(self.kwargs.get('year')) + str(self.kwargs.get('month')) + '.pdf'
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
        calendar_data = self.get_month_calendar()

        #PDF描写
        #スタッフごとのカレンダー
        if calendar_data['staff_obj'] is not None:
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
            self._draw_staff(doc,font,calendar_data)

        #全体カレンダー
        else:
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
            self._draw_all(doc,font,calendar_data)

        # Close the PDF object cleanly, and we're done.
        doc.showPage()
        # pdfを保存
        doc.save()

    #スタッフごとのカレンダー
    def _draw_staff(self, doc, font, calendar_data):

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
                day_position_x = xlist[index_x]+5
                day_position_y = ylist[index_y]+12
                #日付文字
                if self.kwargs.get('month') != day.month:
                    day_text = str(day.month) + "/" + str(day.day)
                else:
                    day_text = str(day.day)

                #土日祝の背景色////////////////////////////////////////////////////
                disp_year  = day.strftime("%Y")
                disp_month = day.strftime("%m").lstrip("0")
                disp_day   = day.strftime("%d").lstrip("0")

                disp_date = disp_year + "/" + disp_month + "/" + disp_day
                if self.kwargs.get('month') == day.month:
                    if disp_date in calendar_data['holidays']() or index_x==0:
                        doc.setFillColor("darkgrey")
                        doc.rect(xlist[index_x]+1,ylist[index_y]+1,20,15,stroke=False,fill=True)
                        doc.setFillColor("white")

                doc.setFont(font,12)
                #当月のみ表示
                if self.kwargs.get('month') == day.month:
                    doc.drawString(day_position_x,day_position_y,day_text)
                #文字色リセット
                doc.setFillColor("black")

                #スケジュール////////////////////////////////////////////////////
                sche_x = day_position_x+28
                sche_y = day_position_y
                doc.setFont(font,8)
                #当月のみ表示
                if self.kwargs.get('month') == day.month:
                    for schedule in schedules:
                        sche_start = localtime(schedule.start_date).strftime("%H:%M")
                        sche_end   = localtime(schedule.end_date).strftime("%H:%M")
                        sche_user  = schedule.careuser.get_short_name()
                        sche_text  = str(sche_start) + "-" + str(sche_end) + " " + sche_user
                        doc.drawString(sche_x,sche_y,sche_text)
                        sche_y+=10
                #フォントサイズを戻す
                doc.setFont(font,10)

    #全体カレンダー
    def _draw_all(self, doc, font, calendar_data):

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
        title = str(self.kwargs.get('year')) + "年" + str(self.kwargs.get('month')) + "月　全体スケジュール"
        doc.drawString(320,30,title)
        #フォントサイズを戻す
        doc.setFont(font,10)

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
                day_position_x = xlist[index_x]+5
                day_position_y = ylist[index_y]+12
                #日付文字
                if self.kwargs.get('month') != day.month:
                    day_text = str(day.month) + "/" + str(day.day)
                else:
                    day_text = str(day.day)

                #土日祝の背景色////////////////////////////////////////////////////
                disp_year  = day.strftime("%Y")
                disp_month = day.strftime("%m").lstrip("0")
                disp_day   = day.strftime("%d").lstrip("0")

                disp_date = disp_year + "/" + disp_month + "/" + disp_day
                if self.kwargs.get('month') == day.month:
                    if disp_date in calendar_data['holidays']() or index_x==0:
                        doc.setFillColor("darkgrey")
                        doc.rect(xlist[index_x]+1,ylist[index_y]+1,20,15,stroke=False,fill=True)
                        doc.setFillColor("white")

                doc.setFont(font,12)
                #当月のみ表示
                if self.kwargs.get('month') == day.month:
                    doc.drawString(day_position_x,day_position_y,day_text)
                #文字色リセット
                doc.setFillColor("black")

                #スケジュール////////////////////////////////////////////////////
                sche_x = day_position_x+28
                sche_y = day_position_y
                doc.setFont(font,8)
                #当月のみ表示
                if self.kwargs.get('month') == day.month:
                    for schedule in schedules:
                        sche_start = localtime(schedule.start_date).strftime("%H:%M")
                        sche_end   = localtime(schedule.end_date).strftime("%H:%M")
                        sche_user  = schedule.careuser.get_short_name()
                        sche_text  = str(sche_start) + "-" + str(sche_end) + " " + sche_user
                        doc.drawString(sche_x,sche_y,sche_text)
                        sche_y+=10
                #フォントサイズを戻す
                doc.setFont(font,10)

        