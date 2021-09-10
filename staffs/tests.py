from django.http import HttpRequest, response
from django.test import TestCase
from staffs.views import top

class TopPageViewTest(TestCase):
    def test_top_returns_200(self):
        request = HttpRequest()
        response = top(request)
        self.assertEqual(response.status_code,200)
    
    def test_top_returns_expected_content(self):
        request = HttpRequest()
        response = top(request)
        self.assertEqual(response.content,b'Hello World')

