import logging

# # Create your models here.
import logging.config
from datetime import datetime
from decimal import Decimal
from typing import Optional

from django.conf import settings
from django.db import models
from django.db.models import F, Q, Window
from django.db.models.functions import Rank
from django.forms.models import model_to_dict


from stock.models.site_model import SiteInfo

from wcommon.templatetags import done_type_map

logging.config.dictConfig(settings.LOGGING)

logger = logging.getLogger(__name__)


class MonthData(models.Model):
    year = models.IntegerField(default=2010, verbose_name="年")
    month = models.IntegerField(default=1, verbose_name="月份")

    class Meta:
        unique_together = ("year", "month")
        abstract = True


class MonthReport(MonthData):
    siteinfo = models.ForeignKey(
        SiteInfo,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        verbose_name="地點",
    )
    edit_date = models.DateTimeField(default=datetime.now)
    done_type = models.IntegerField(default=0, choices=done_type_map)
    remark = models.TextField(null=True, verbose_name="說明")
    is_done = models.BooleanField(default=False, verbose_name="結案")

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

        if report:
            if f"{report.year}{report.month:02d}" < f"{year}{month:02d}":
                report.pk = None
                report.year = year
                report.month = month
            report.save()
        else:
            report = cls.objects.create(
                siteinfo=site,
                year=year,
                month=month,
            )

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

        ids = [item["id"] for item in query_set]
        return (
            cls.objects.select_related("siteinfo")
            .filter(id__in=ids)
            .filter(is_done=is_done)
            .all()
        )


    @classmethod
    def update_column_value(cls, id: int, is_add: bool, column: str, value: Decimal):
        item = cls.objects.get(id=id)
        original_value = getattr(item,column)
        original_value +=  value if is_add else -value
        setattr(item,column,original_value)
        item.save()

    @classmethod
    def update_edit_date(cls, id: int):
        # 获取当前时间
        now = datetime.now()
        update_data = {
            "edit_date": now,  # 更新编辑日期
            "year": now.year,  # 更新年份
            "month": now.month,  # 更新月份
        }
        # 执行更新操作
        cls.objects.filter(id=id).update(**update_data)

    def get_column_decimal_val(self, column: str):
        float_value = getattr(self, column)
        if isinstance(float_value, float):
            float_value = Decimal(str(float_value))
        return float_value

    class Meta:
        unique_together = ("siteinfo", "year", "month", "done_type", "is_done")
        abstract = True
