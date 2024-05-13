from datetime import datetime
from decimal import Decimal
from django.db import models
from django.forms import model_to_dict

from stock.models.material_model import Materials
from stock.models.monthreport_model import MonthData
from stock.models.site_model import SiteInfo
from stock.models.stock_model import Stock

class SteelPillar(MonthData):
    edit_date = models.DateTimeField(default=datetime.now)
    mat_code = models.CharField(max_length=10, default="", verbose_name="物料代號")
    for i in range(1, 18):
        locals()[f"l_{i}"] = models.IntegerField(default=0, verbose_name=f"In_{i}")
    total = models.IntegerField(default=0, verbose_name="總計")

    @classmethod
    def get_value(cls, mat_code, year, month):
        sp, _ = cls.objects.get_or_create(mat_code=mat_code, year=year, month=month)
        return sp


    @classmethod
    def add_report(
        cls,
        build_date: datetime,
        mat: Materials,
    ):
        y, m = build_date.year ,build_date.month
        cls.update_value(mat,y,m)

    @classmethod
    def update_value(cls, mat: Materials, year, month):
        if mat.mat_code not in ("301", "351", "401"):
            return
        sp, _ = cls.objects.get_or_create(mat_code=mat.mat_code, year=year, month=month)
        stock = Stock.getItem(SiteInfo.get_warehouse(), mat)
        setattr(sp, f"l_{mat.specification.id}", stock.quantity)

        sp.save()

    class Meta:
        unique_together = ["year", "month", "mat_code"]
