from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics

# Create the HttpResponse object with the appropriate PDF headers.
def index(request):
    response = HttpResponse(content_type='application/pdf')
    file_pdf = "example01.pdf"
    response['Content-Disposition'] = 'attachment; filename=' + file_pdf
    # Create the PDF object, using the response object as its "file."
    pp = canvas.Canvas(response)
    fontname_g = "HeiseiKakuGo-W5"
    pdfmetrics.registerFont (UnicodeCIDFont (fontname_g))
    pp.setFont(fontname_g,16)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    pp.drawString(100, 800, "Hello world.")
    pp.drawString(100, 700, "こんにちは")
    # Close the PDF object cleanly, and we're done.
    pp.showPage()
    pp.save()
    return response