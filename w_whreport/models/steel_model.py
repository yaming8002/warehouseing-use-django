from datetime import datetime
from decimal import Decimal

from django.db import models
from typing import Optional
from w_stock.models.material_model import Materials
from w_whreport.models.monthreport_model import MonthReport
from w_stock.models.site_model import SiteInfo
from django.db.models import Q
import logging

# # Create your models here.
import logging.config
from django.conf import settings

logging.config.dictConfig(settings.LOGGING)

logger = logging.getLogger(__name__)


class BaseSteelReport(MonthReport):
    static_column_code = {
        "358": "H300*300",
        "352": "H300中柱",
        "295": "H350*350",
        "400": "H350中柱",
        "424": "H400*400",
        "367": "H400中柱",
        "170": "H408*400",
        "193": "H414*405",
        "265": "H414中柱",
        "102": "覆工板",
        "18": "千斤頂",
        "19": "土壓計",
    }

    for k, v in static_column_code.items():
        locals()[f"m_{k}"] = models.DecimalField(
            max_digits=10, decimal_places=2, default=0.0, verbose_name=v
        )

    class Meta:
        abstract = True


class SteelReport(BaseSteelReport):

    @classmethod
    def get_current_by_site(
        cls, site: SiteInfo, year: Optional[int] = None, month: Optional[int] = None
    ):
        if not year:
            now = datetime.now()
            year, month = now.year, now.month

        query = Q(siteinfo=site) & (Q(year__lt=year) | Q(year=year, month__lte=month))
        # print( cls.objects.filter(query).order_by('-year', '-month').query)
        report = cls.objects.filter(query).order_by("-year", "-month").first()

        if not report or ( report.is_done  and f"{report.year}{report.month:02d}" < f"{year}{month:02d}" ):
            report = cls.objects.create(
                siteinfo=site,
                year=year,
                month=month,
            )
        else:
            if f"{report.year}{report.month:02d}" < f"{year}{month:02d}":
                report.pk = None
                report.year = year
                report.month = month
            report.save()

        return report

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
        if mat.id not in cls.static_column_code.keys():
            return

        year, month = build_date.year, build_date.month
        report = cls.get_current_by_site(site, year, month)
        whse = cls.get_current_by_site(SiteInfo.get_site_by_code("0001"), year, month)

        value = all_unit if mat.is_divisible else all_quantity
        value = Decimal(value)
        cls.update_column_value(whse.id, not is_in, f"m_{mat.id}", value)
        cls.update_column_value(report.id, not is_in, f"m_{mat.id}", value)


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
