from django.contrib.auth.mixins import UserPassesTestMixin

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class StaffUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff