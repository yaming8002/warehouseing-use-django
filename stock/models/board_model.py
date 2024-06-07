from datetime import datetime
from decimal import Decimal
from typing import Optional

from django.db import models
from django.db.models import F, Q, Window
from django.db.models.functions import Rank
from django.forms import model_to_dict

from stock.models.material_model import Materials
from stock.models.monthreport_model import MonthReport
from stock.models.site_model import SiteInfo
from decimal import ROUND_HALF_UP
import logging

# # Create your models here.
import logging.config
from django.conf import settings

from wcom.utils.uitls import get_before_year_month

logging.config.dictConfig(settings.LOGGING)

logger = logging.getLogger(__name__)


class BoardReport(MonthReport):
    static_column_code = {
        "22": "鋪路鐵板 全",
        "2205": "鋪路鐵板 半",
        "92": "簍空覆工板",
        "95": "洗車板",
    }

    is_lost = models.BooleanField(default=False, verbose_name="是否遺失")

    mat_code = models.CharField(
        max_length=5, default="22", verbose_name="物料(預設鐵板 全)"
    )
    mat_code2 = models.CharField(
        max_length=5, null=True, verbose_name="物料(預設鐵板半)"
    )

    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="數量"
    )

    quantity2 = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="數量2"
    )

    close = models.BooleanField(default=False, null=True, verbose_name="關閉")

    class Meta:
        unique_together = (
            "siteinfo",
            "year",
            "month",
            "done_type",
            "is_done",
            "mat_code",
        )

    @classmethod
    def get_site_matial(
        cls,
        site: SiteInfo,
        mat_code: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        is_done: bool = False,
    ):
        # 如果没有提供年份和月份，使用当前的年份和月份
        if not year or not month:
            now = datetime.now()
            year, month = now.year, now.month

        # 构建查询条件

        query = Q(mat_code=mat_code) & Q(siteinfo=site) & Q(is_done=is_done)  & (Q(year__lt=year) | Q(year=year, month__lte=month))
        # 尝试查找当前年份和月份的记录
        report = cls.objects.filter(query).order_by("-year", "-month").first()

        # 如果没有找到当前年份和月份的记录，查找更早的记录
        if report:
            if f"{report.year}{report.month:02d}" < f"{year}{month:02d}":
                report.pk = None
                report.year = year
                report.month = month
                report.save()
        else:
            # 如果没有找到更早的记录，创建新的记录
            report= cls.objects.create(
                siteinfo=site,
                year=year,
                month=month,
                mat_code=mat_code,
                is_done=is_done
            )

              # 设置 mat_code2 的值
        report.mat_code2 = '2205' if mat_code == '22' else None
        report.save()
        return report

    @classmethod
    def get_current_by_query(cls, query, is_done=False):
        query_set = (
            cls.objects.annotate(
                rank=Window(
                    expression=Rank(),
                    partition_by=[F("siteinfo__id")],
                    order_by=[F("year").desc(), F("month").desc()],
                )
            )
            .filter(rank=1)
            .filter(query)
            .order_by("-year", "-month")
            .values("id", "siteinfo__id")
        )
        # print(query_set.query)
        ids = [item["id"] for item in query_set]

        return (
            cls.objects.select_related("siteinfo")
            .filter(id__in=ids)
            .filter(is_done=is_done)
            .filter(close=False)
            .filter( ~( Q(quantity=0) & Q(quantity2=0)) )
            .order_by("done_type", "siteinfo__code", "siteinfo__genre")
            .all()
        )

    @classmethod
    def update_column_value_by_before(
        cls,
        site: SiteInfo,
        year: int,
        month: int,
        is_add: bool,
        column: str,
        value: Decimal,
    ):
        find_code = "22" if column == "2205" else column
        target_field = "quantity2" if column == "2205" else "quantity"

        now = cls.get_site_matial(site, find_code, year, month)
        b_year, b_month = get_before_year_month(year, month)
        before = cls.get_site_matial(site, find_code, b_year, b_month)

        if column in ["22", "2205"]:
            now.mat_code2 = "2205"

        new_value = getattr(before,target_field) 
        new_value += value if is_add else -value
        setattr(now, target_field, new_value)

        if now.quantity + now.quantity2 == 0:
            now.close = True
        else:
            now.close = False
        now.save()
