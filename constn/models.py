from django.db import models
from wcommon.templatetags import constn_state
from django.utils import timezone

from whse.models.material import MatList
from whse.models.whse import Stock, StockBase


# Create your models here.
class Construction(models.Model):
    code = models.CharField(max_length=30, verbose_name="工地代號")
    owner = models.CharField(max_length=50, verbose_name="業主")
    name = models.CharField(max_length=50, default= '', verbose_name="工程名稱")
    address = models.TextField(verbose_name="地點")
    crate_date = models.DateField(default=timezone.now, verbose_name="發案日期")
    member = models.CharField(max_length=10, blank=True, null=True, verbose_name="現場人員")
    counter = models.CharField(max_length=10, blank=True, null=True, verbose_name="會計人員")
    company = models.CharField(max_length=10, blank=True, null=True, verbose_name="公司行號")
    state = models.IntegerField(default=2, choices=constn_state) 
    done_date = models.DateField(null=True, verbose_name="結案日期")

    class Meta:
        unique_together = ("code", "name","address")
        
    def __str__(self):
        return self.code

class ConStock(StockBase):
    construction = models.ForeignKey(Construction, on_delete=models.CASCADE, verbose_name="工地")

    class Meta:
        unique_together = ("construction", "materiel")