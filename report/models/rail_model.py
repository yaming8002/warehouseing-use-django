from datetime import datetime
from decimal import Decimal

from django.db import models, transaction
from django.db.models import F

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
            # 获取当前年份和月份

        site = translog.constn_site
        year, month = translog.build_date.year, translog.build_date.month
        report = cls.get_current_by_site(site, year, month)
        whse = cls.get_current_by_site(SiteInfo.objects.get(code="0001"), year, month)

        if is_in:
            setattr(
                report,
                f"in_{mat.specification.id}",
                report.get_column_decimal_val(f"in_{mat.specification.id}")
                + all_quantity,
            )
            setattr(
                whse,
                f"in_{mat.specification.id}",
                whse.get_column_decimal_val(f"in_{mat.specification.id}")
                + all_quantity,
            )
        else:
            setattr(
                report,
                f"out_{mat.specification.id}",
                report.get_column_decimal_val(f"out_{mat.specification.id}")
                + all_quantity,
            )
            setattr(
                whse,
                f"in_{mat.specification.id}",
                whse.get_column_decimal_val(f"in_{mat.specification.id}")
                - all_quantity,
            )

        report.save()
        whse.save()
