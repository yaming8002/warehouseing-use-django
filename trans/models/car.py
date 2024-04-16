from decimal import Decimal ,ROUND_HALF_UP
from django.db import models
from datetime import datetime
from django.db.models import Q
from stock.models.material_model import Materials
from stock.models.site_model import SiteInfo
from wcommon.utils.uitls import excel_value_to_str, get_month_range


# Create your models here.
class CarInfo(models.Model):
    car_number = models.CharField(max_length=15, verbose_name="車牌")
    firm = models.CharField(max_length=30, default="", verbose_name="公司")
    is_count = models.BooleanField(default=True, verbose_name="報價")
    value = models.DecimalField(
        max_digits=10, default=0, decimal_places=2, verbose_name="基本台金額", null=True
    )
    remark = models.CharField(max_length=150,verbose_name="噸數(備註)", default="", null=True)

    @classmethod
    def create(cls, car_number, firm=None, remark=None, value=None):
        if car_number is None:
            return None
        elif firm is None and cls.objects.filter(car_number=car_number).exists():
            return cls.objects.get(car_number=car_number)
        elif firm is None:
            return cls.objects.create(
                car_number=car_number, remark=remark, is_count=False
            )
        else:
            query = Q(car_number=car_number, firm=firm)
            if cls.objects.filter(query).exists():
                return cls.objects.get(query)

        return cls.objects.create(car_number=car_number, firm=firm, remark=remark)

    class Meta:
        unique_together = ["car_number", "firm"]
        ordering = ["-firm", "car_number"]  # 按照 id 升序排序

    def __str__(self):
        return f"{self.car_number} 公司:{self.firm} "