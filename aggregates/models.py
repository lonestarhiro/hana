from django.db import models
from django.conf import settings

class DataLockdate(models.Model):
     
    lock_date      = models.DateTimeField(verbose_name="データロック最終日時")
    updated_by     = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name="更新者",on_delete=models.RESTRICT)
    updated_at     = models.DateTimeField(verbose_name="更新日",auto_now=True)

    def __str__(self):
        return f"{self.end_date}"
