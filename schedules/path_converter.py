class FourDigitYearConverter:
    regex = '[0-9]{4}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%04d' % value
        
class TweDigitMonthConverter:
    regex = '0?[1-9]|1[0-2]'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%02d' % value