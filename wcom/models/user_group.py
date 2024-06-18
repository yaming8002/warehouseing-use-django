
from django.db import models


class UserGroup(models.Model):
    name = models.CharField(max_length=50, verbose_name="名稱")
    is_active = models.BooleanField(default="True")

    def __str__(self):
        return  self.name

    class Meta:
        verbose_name = "ugroup"
        verbose_name_plural = "ugroups"

