from decimal import Decimal

from django.db import models
from stock.models.material_model import Materials
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
    def add_report(
        cls, site: SiteInfo, build_date, is_in: bool, mat: Materials, all_quantity: Decimal
    ):
        if mat.mat_code != "3050":
            return
        year, month = build_date.year, build_date.month
        report = cls.get_current_by_site(site, year, month)
        whse = cls.get_current_by_site(SiteInfo.objects.get(code="0001"), year, month)
        if is_in:
            column = f"in_{mat.specification.id}"
            total_col = "in_total"
        else:    
            column = f"out_{mat.specification.id}"
            total_col = "out_total"
        
        cls.update_column_value(report.id,True,column,all_quantity)
        cls.update_column_value(report.id,True,total_col,all_quantity)
        cls.update_column_value(whse.id,is_in,f"in_{mat.specification.id}",all_quantity)
