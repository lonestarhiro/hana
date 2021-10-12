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
    date_field = "start_date"

    title = '月間予定表'
    font_name = 'HeiseiMin-W3'
    is_bottomup = False

    def get(self,request, *args, **kwargs):

        filename = str(self.kwargs.get('year')) + str(self.kwargs.get('month')) + '.pdf'
        #print(self.kwargs.get('year'))
        # pdf用のContent-TypeやContent-Dispositionをセット
        response = HttpResponse(status=200, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        # 即ダウンロードしたい時は、attachmentをつける
        # response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.filename)

        # A4縦書きのpdfを作る
        size = landscape(A4)
        # pdfを描く場所を作成：位置を決める原点は左上にする(bottomup)
        doc = canvas.Canvas(response, pagesize=size,bottomup=self.is_bottomup)
        # 日本語が使えるゴシック体のフォントを設定する
        pdfmetrics.registerFont(UnicodeCIDFont(self.font_name))
        doc.setFont(self.font_name,10)
        # pdfのタイトルを設定
        doc.setTitle(self.title)
        # pdf上にも、タイトルとして使用したクラス名を表示する
        #doc.drawString(10*mm, 10*mm, __class__.__name__)

        self._staff_schedule_draw(doc)
        return response

    def _staff_schedule_draw(self, doc, *args, **kwargs):

        calendar_data = self.get_month_calendar()
        # 複数行の表を用意したい場合、二次元配列でデータを用意する
        #data = [
        #    ['行1-列1', '行1-列2-*********', '行1-列3-*********-*********'],
        #    ['行2-列1', '行2-列2-*********', '行2-列3-*********-*********'],
        #    ['行3-列1', '行3-列2-*********', '行3-列3-*********-*********'],
        #]

        #table = Table(data)
        # TableStyleを使って、Tableの装飾をします
        #table.setStyle(TableStyle([
            # 表で使うフォントとそのサイズを設定
        #    ('FONT', (0, 0), (-1, -1), self.font_name, 9),
            # 四角に罫線を引いて、0.5の太さで、色は黒
        #    ('BOX', (0, 0), (-1, -1), 1, colors.black),
            # 四角の内側に格子状の罫線を引いて、0.25の太さで、色は赤
        #    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.red),
            # セルの縦文字位置を、TOPにする
            # 他にMIDDLEやBOTTOMを指定できるのでお好みで
        #    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        #]))

        # tableを描き出す位置を指定
        #table.wrapOn(doc, 50*mm, 10*mm)
        #table.drawOn(doc, 50*mm, 10*mm)

        #タイトル
        doc.setFont(self.font_name,14)
        if calendar_data['staff_obj'] is not None:
            title = str(self.kwargs.get('year')) + "年" + str(self.kwargs.get('month')) + "月　" + str(calendar_data['staff_obj']) + " 様　月間スケジュール"
            doc.drawString(280,30,title)
        else:
            title = str(self.kwargs.get('year')) + "年" + str(self.kwargs.get('month')) + "月　全体スケジュール"
            doc.drawString(320,30,title)
        #フォントサイズを戻す
        doc.setFont(self.font_name,10)

        xlist = (30,142,254,365,478,590,702,812)

        #表示する週の数によって分岐
        if len(calendar_data['month_day_schedules']) <6:
            #5週Ver
            ylist = (40,55,158,261,364,467,570)
        else:
            #6週Ver
            ylist = (40,55,141,227,313,399,485,571)
        #罫線描写
        doc.grid(xlist, ylist)

        #曜日
        doc.drawString((xlist[1]+xlist[0])/2-5,52,"日")
        doc.drawString((xlist[2]+xlist[1])/2-5,52,"月")
        doc.drawString((xlist[3]+xlist[2])/2-5,52,"火")
        doc.drawString((xlist[4]+xlist[3])/2-5,52,"水")
        doc.drawString((xlist[5]+xlist[4])/2-5,52,"木")
        doc.drawString((xlist[6]+xlist[5])/2-5,52,"金")
        doc.drawString((xlist[7]+xlist[6])/2-5,52,"土")
        
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

                doc.setFont(self.font_name,12)
                #当月のみ表示
                if self.kwargs.get('month') == day.month:
                    doc.drawString(day_position_x,day_position_y,day_text)
                #文字色リセット
                doc.setFillColor("black")

                #スケジュール////////////////////////////////////////////////////
                sche_x = day_position_x+28
                sche_y = day_position_y
                doc.setFont(self.font_name,8)
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
                doc.setFont(self.font_name,10)

        # Close the PDF object cleanly, and we're done.
        doc.showPage()
        # pdfを保存
        doc.save()

        