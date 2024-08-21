from datetime import datetime
from decimal import Decimal
import sys

from django.db import models, transaction
from django.forms import model_to_dict

from stock.models.material_model import Materials
from stock.models.monthreport_model import MonthReport
from stock.models.site_model import SiteInfo
from stock.models.stock_model import Stock
from wcom.utils.uitls import get_year_month
import logging

# # Create your models here.
import logging.config
from django.conf import settings

logging.config.dictConfig(settings.LOGGING)

logger = logging.getLogger(__name__)


class BaseSteelReport(MonthReport):
    static_column_code = {
        "300": "H300*300",
        "301": "H300中柱",
        "350": "H350*350",
        "351": "H350中柱",
        "390": "H390*400",
        "400": "H400*400",
        "401": "H400中柱",
        "408": "H408*400",
        "414": "H414*405",
        "4141": "H414中柱",
        "92": "覆工板",
        "12": "千斤頂",
        "13": "土壓計",
    }

    for k, v in static_column_code.items():
        locals()[f"m_{k}"] = models.DecimalField(
            max_digits=10, decimal_places=2, default=0.0, verbose_name=v
        )
    class Meta:
        abstract = True


class SteelReport(BaseSteelReport) :

    @classmethod
    def add_report(
        cls,
        site: SiteInfo,
        build_date: datetime,
        is_in: bool,
        mat: Materials,
        all_quantity: Decimal,
        all_unit: Decimal,
    ):
        if mat.mat_code not in cls.static_column_code.keys():
            return

        year, month = build_date.year, build_date.month
        report = cls.get_current_by_site(site, year, month)
        whse = cls.get_current_by_site(SiteInfo.get_site_by_code("0001"), year, month)

        value = all_unit if mat.is_divisible else all_quantity
        value = Decimal(value)
        cls.update_column_value(whse.id, not is_in, f"m_{mat.mat_code}", value)
        cls.update_column_value(report.id, not is_in, f"m_{mat.mat_code}", value)


class SteelColumn(models.Model):
    report = models.ForeignKey(
        SteelReport,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        verbose_name="report",
    )
    material = models.ForeignKey(
        Materials, on_delete=models.CASCADE, verbose_name="物料"
    )
    all_quantity = models.IntegerField(default=0, verbose_name="總數量")

    class Meta:
        unique_together = ["report", "material", "all_quantity"]
        ordering = ["id"]  # 按照 id 升序排序

# class SteelItem(MonthReport):
#     steel = models.ForeignKey(
#         SteelReport,
#         on_delete=models.SET_NULL,
#         null=True,
#         default=None,
#         verbose_name="地點",
#     )

#     year = models.IntegerField(default=2010, verbose_name="年")
#     month = models.IntegerField(default=1, verbose_name="月份")

#     material = models.ForeignKey(
#         Materials, on_delete=models.CASCADE, verbose_name="物料"
#     )

#     all_quantity = models.IntegerField(default=0, verbose_name="總數量")

#     class Meta:
#         unique_together = ["steel", "material", "all_quantity"]
#         ordering = ["id"]  # 按照 id 升序排序
