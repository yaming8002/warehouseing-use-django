from decimal import Decimal

from django.db import models
from stock.models.monthreport_model import MonthReport
from stock.models.site_model import SiteInfo

# # Create your models here.

class RailReport(MonthReport):
    for i in range(5, 17):
        locals()[f"in_{i}"] = models.DecimalField(
            max_digits=10, decimal_places=2, default=0.0, verbose_name=f"in_{i}"
        )
        locals()[f"out_{i}"] = models.DecimalField(
            max_digits=10, decimal_places=2, default=0.0, verbose_name=f"out_{i}"
        )
    in_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="入庫總計"
    )
    out_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="出庫總計"
    )
    rail_ng = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="廢鐵"
    )

    @classmethod
    def count_total(cls , site: SiteInfo,year:int,month:int,is_in:bool=False):
        now = cls.get_current_by_site(site,year, month)
        column = "in_" if is_in else "out_"
        value = Decimal(0)
        for i in range(5,17):
            value += getattr(now,f"{column}{i}",0)

        if is_in :
            now.in_total = value
        else:
            now.out_total = value
        now.save()
        return now
