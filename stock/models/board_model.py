from datetime import datetime
from decimal import Decimal
from typing import Optional

from django.db import models
from django.db.models import F, Q ,Window
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

    is_lost =models.BooleanField(default=False,verbose_name="是否遺失")

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

    @classmethod
    def get_board_report(cls, site, mat):
        # 简化mat_code逻辑
        mat_code = "22" if mat.mat_code in ["22", "2205"] else mat.mat_code
        mat_code2 = "2205" if mat.mat_code in ["22", "2205"] else None

        # 使用 get_or_create 方法简化对象获取或创建逻辑
        obj, _ = cls.objects.get_or_create(
            siteinfo=site, mat_code=mat_code, defaults={"mat_code2": mat_code2}
        )
        return obj
    
    class Meta:
        unique_together = ("siteinfo", "year", "month", "done_type", "is_done","remark")


    @classmethod
    def get_site_matial(
        cls, site: SiteInfo,mat_code:str, year: Optional[int] = None, month: Optional[int] = None, is_done: bool=False
    ):
        if not year:
            now = datetime.now()
            year, month = now.year, now.month

        query = Q(mat_code=mat_code) & Q(siteinfo=site)& Q(is_done=is_done) & (Q(year__lt=year) | Q(year=year, month__lte=month) )
        # print( cls.objects.filter(query).order_by('-year', '-month').query)
        if cls.objects.filter(query).exists() :
            report = cls.objects.filter(query).order_by("-year", "-month").first()
            if f"{report.year}{report.month:02d}" < f"{year}{month:02d}":
                report.pk = None
                report.year = year
                report.month = month
            report.save()
        else:
         return None
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
        print(query_set.query)
        ids = [item["id"] for item in query_set]
        
        return (
            cls.objects.select_related("siteinfo")
            .filter(id__in=ids)
            .filter(is_done=is_done)
            .order_by("done_type","siteinfo__code","siteinfo__genre")
            .all()
        )

    @classmethod
    def update_column_value_by_before(cls, site: SiteInfo, year: int, month: int, is_add: bool, column: str, value: Decimal):
        # Get the previous year and month
        b_year, b_month = get_before_year_month(year, month)
        find_code = '22' if column =='2205' else column
        before = cls.get_site_matial(site,find_code, b_year, b_month)
        now = cls.get_site_matial(site,find_code, year, month)
        # Retrieve the records for the previous and current periods
        if now is None:
            now = cls(
                siteinfo=site,
                year=year,
                month=month,
            )
        # Set material codes based on conditions
        if column in ['22', '2205']:
            now.mat_code = '22'
            now.mat_code2 = '2205'
        else:
            now.mat_code = column
            now.mat_code2 = None

        # Choose the right quantity field based on column and adjust its value
        target_field = 'quantity2' if column == '2205' else 'quantity'
        previous_quantity = getattr(before, target_field,0) 
        change = value if is_add else -value
        print(f"{now.quantity} + {change} = {Decimal(previous_quantity) + change}")

        new_quantity = Decimal(previous_quantity) + change

        # Set the updated quantity
        setattr(now, target_field, new_quantity)
        print(f"{now.quantity} += {change}")
        # Save the updated record
        now.save()

    @classmethod
    def add_report(
        cls,
        site: SiteInfo,
        remark: str,
        is_in: bool,
        mat: Materials,
        all_quantity: Decimal,
    ):
        if mat.mat_code not in cls.static_column_code.keys() or (
            mat.mat_code == "11" and "簍空" not in remark
        ):
            return

        report = cls.get_board_report(site, mat)
        whse = cls.get_board_report(SiteInfo.objects.get(code="0001"), mat)
        code_str = "quantity2" if mat.mat_code == "2205" else "quantity"

        cls.update_column_value(report.id, not is_in, code_str, all_quantity)
        cls.update_column_value(whse.id, is_in, code_str, all_quantity)
        cls.update_edit_date(report.id)
        cls.update_edit_date(whse.id)

    class Meta:
        unique_together = (
            "siteinfo",
            "year",
            "month",
            "done_type",
            "is_done",
            "mat_code",
        )
