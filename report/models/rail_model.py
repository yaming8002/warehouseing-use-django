from datetime import datetime
from decimal import Decimal

from django.db import models, transaction
from django.db.models import F
from django.forms import model_to_dict

from stock.models.material import Materials
from stock.models.site import SiteInfo

# # Create your models here.

from report.models.monthreport_model import MonthReport
from trans.models.trans import TransLog
import sys


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
    def add_report(
        cls, translog: TransLog, is_in: bool, mat: Materials, all_quantity: Decimal
    ):
        if mat.mat_code != "3050":
            return
        site = translog.constn_site
        year, month = translog.build_date.year, translog.build_date.month
        report = cls.get_current_by_site(site, year, month)
        whse = cls.get_current_by_site(SiteInfo.objects.get(code="0001"), year, month)
        column = f"in_{mat.specification.id}"  if is_in else f"out_{mat.specification.id}"
        if translog.constn_site.code=='1565':
            print(model_to_dict(report))
            print(f"in_{mat.specification.id}")
            print(all_quantity)

        cls.update_column_value(report.id,True,column,all_quantity)
        cls.update_column_value(whse.id,is_in,f"in_{mat.specification.id}",all_quantity)
        report.save()
        whse.save()
