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
class CalendarView(MonthWithScheduleMixin,View):
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
        calendar_data = self.get_month_data()

        #PDF描写
        #全体のカレンダー
        if calendar_data['staff_obj'] is None and calendar_data['careuser_obj'] is None:
            self._draw_all(response,calendar_data)
        #スタッフカレンダー
        elif calendar_data['staff_obj'] is not None:
            self._draw_staff(response,calendar_data)
        #利用者カレンダー
        elif calendar_data['careuser_obj'] is not None:
            self._draw_careuser(response,calendar_data)

    #スタッフごとのカレンダー
    def _draw_staff(self, response, calendar_data):

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
                        if len(disp_day)==1:
                            doc.rect(xlist[index_x]+1,ylist[index_y]+1,15,15,stroke=False,fill=True)
                        else:
                            doc.rect(xlist[index_x]+1,ylist[index_y]+1,21,15,stroke=False,fill=True)
                        doc.setFillColor("white")

                doc.setFont(font,12)
                #当月のみ表示
                if self.kwargs.get('month') == day.month:
                    doc.drawString(day_position_x,day_position_y,day_text)
                #文字色リセット
                doc.setFillColor("black")

                #スケジュール////////////////////////////////////////////////////
                sche_x = day_position_x+22
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
        doc.showPage()
        # pdfを保存
        doc.save()

    #全体カレンダー
    def _draw_all(self, response, calendar_data):

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
                disp_year  = day.strftime("%Y")
                disp_month = day.strftime("%m").lstrip("0")
                disp_day   = day.strftime("%d").lstrip("0")

                disp_date = disp_year + "/" + disp_month + "/" + disp_day
                if self.kwargs.get('month') == day.month:
                    if disp_date in calendar_data['holidays']() or index_x==0:
                        doc.setFillColor("darkgrey")
                        if len(disp_day)==1:
                            doc.rect(xlist[index_x]+1,ylist[index_y]+1,15,15,stroke=False,fill=True)
                        else:
                            doc.rect(xlist[index_x]+1,ylist[index_y]+1,21,15,stroke=False,fill=True)

                        doc.setFillColor("white")

                doc.setFont(font,12)
                #当月のみ表示
                if self.kwargs.get('month') == day.month:
                    doc.drawString(day_position_x,day_position_y,day_text)
                #文字色リセット
                doc.setFillColor("black")

                #スケジュール////////////////////////////////////////////////////
                sche_x = day_position_x+5
                sche_y = day_position_y+12
                doc.setFont(font,8)
                #当月のみ表示
                if self.kwargs.get('month') == day.month:
                    for schedule in schedules:
                        sche_start = localtime(schedule.start_date).strftime("%H:%M")
                        sche_end   = localtime(schedule.end_date).strftime("%H:%M")
                        sche_user  = schedule.careuser.get_short_name()
                        sche_staff = ""
                        if(schedule.staff1):sche_staff += str(schedule.staff1.get_short_name())
                        if(schedule.staff2):sche_staff += " " + str(schedule.staff2.get_short_name())
                        if(schedule.staff3):sche_staff += " " + str(schedule.staff3.get_short_name())
                        if(schedule.staff4):sche_staff += " " + str(schedule.staff4.get_short_name())

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
    def _draw_careuser(self, response, calendar_data):

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
                        if len(disp_day)==1:
                            doc.rect(xlist[index_x]+1,ylist[index_y]+1,15,15,stroke=False,fill=True)
                        else:
                            doc.rect(xlist[index_x]+1,ylist[index_y]+1,21,15,stroke=False,fill=True)
                        doc.setFillColor("white")

                doc.setFont(font,12)
                #当月のみ表示
                if self.kwargs.get('month') == day.month:
                    doc.drawString(day_position_x,day_position_y,day_text)
                #文字色リセット
                doc.setFillColor("black")

                #スケジュール////////////////////////////////////////////////////
                sche_x = day_position_x+18
                sche_y = day_position_y+3
                doc.setFont(font,11)
                #当月のみ表示
                if self.kwargs.get('month') == day.month:
                    for schedule in schedules:

                        sche_staff = ""
                        if(schedule.staff1):sche_staff += str(schedule.staff1.get_short_name())
                        if(schedule.staff2):sche_staff += "・" + str(schedule.staff2.get_short_name())
                        if(schedule.staff3):sche_staff += "・" + str(schedule.staff3.get_short_name())
                        if(schedule.staff4):sche_staff += "・" + str(schedule.staff4.get_short_name())

                        if schedule.peoples>1:
                            sche_start = localtime(schedule.start_date).strftime("%H:%M")
                            sche_end   = localtime(schedule.end_date).strftime("%H:%M")
                            sche_text  = str(sche_start) + "-" + str(sche_end)
                            doc.drawString(sche_x,sche_y,sche_text)

                            name_x=sche_x+5
                            sche_y+=13
                            sche_text  = sche_staff
                            doc.drawString(name_x,sche_y,sche_text)
                            sche_y+=13
                        elif len(sche_staff)>2:
                            sche_start = localtime(schedule.start_date).strftime("%H:%M")
                            sche_end   = localtime(schedule.end_date).strftime("%H:%M")
                            text0_2 = sche_staff[0:2]
                            sche_text  = str(sche_start) + "-" + str(sche_end) + "  " + str(text0_2)
                            doc.drawString(sche_x,sche_y,sche_text)

                            name_x=sche_x+60
                            sche_y+=12
                            sche_text  = sche_staff[2:]
                            doc.drawString(name_x,sche_y,sche_text)
                            sche_y+=13

                        else:
                            sche_start = localtime(schedule.start_date).strftime("%H:%M")
                            sche_end   = localtime(schedule.end_date).strftime("%H:%M")
                            sche_text  = str(sche_start) + "-" + str(sche_end) + "  " + sche_staff
                            doc.drawString(sche_x,sche_y,sche_text)
                            sche_y+=13
                #フォントサイズを戻す
                

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