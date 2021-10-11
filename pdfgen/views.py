from schedules.models import Schedule
from django.http import HttpResponse
from django.views import View
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin,MonthWithScheduleMixin
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

#以下staffuserのみ表示（下のStaffUserRequiredMixinにて制限中）
class CalendarView(StaffUserRequiredMixin,MonthWithScheduleMixin,View):
    model = Schedule
    date_field = "start_date"

    def get(self,request, *args, **kwargs):

        filename = str(self.kwargs.get('year')) + str(self.kwargs.get('month')) + '.pdf'
        title = '月間予定表'
        font_name = 'HeiseiKakuGo-W5'
        is_bottomup = False

        #print(self.kwargs.get('year'))
        # pdf用のContent-TypeやContent-Dispositionをセット
        response = HttpResponse(status=200, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        # 即ダウンロードしたい時は、attachmentをつける
        # response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.filename)

        # A4縦書きのpdfを作る
        size = landscape(A4)
        # pdfを描く場所を作成：位置を決める原点は左上にする(bottomup)
        doc = canvas.Canvas(response, pagesize=size,bottomup=is_bottomup)
        # 日本語が使えるゴシック体のフォントを設定する
        pdfmetrics.registerFont(UnicodeCIDFont(font_name))
        doc.setFont(font_name,16)
        # pdfのタイトルを設定
        doc.setTitle(title)
        # pdf上にも、タイトルとして使用したクラス名を表示する
        #doc.drawString(10*mm, 10*mm, __class__.__name__)

        self._draw(doc)
        return response

    def _draw(self, doc):

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

        xlist = (30,142,254,365,478,590,702,812)
        #5週Ver
        ylist = (50,180,310,440,570)
        #6週Ver
        ylist = (50,136,222,308,394,480,566)
        doc.grid(xlist, ylist)

        doc.drawString(0,20, "Hello world.")
        doc.drawString(800, 300, "こんにちは")
        # Close the PDF object cleanly, and we're done.
        doc.showPage()

        # pdfを保存
        doc.save()

        