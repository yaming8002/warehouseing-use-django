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

from wcom.templatetags import done_type_map
from wcom.utils.uitls import get_before_year_month

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
    remark = models.CharField( max_length=255, null=True, verbose_name="說明")
    is_done = models.BooleanField(default=False, verbose_name="結案")

    @classmethod
    def get_field_names(cls):
        return [f.name for f in cls._meta.fields if f.name not in ['id', 'site', 'year', 'month']]

    @classmethod
    def update_or_create_data(cls, site, year, month):
        if not year:
            now = datetime.now()
            year, month = now.year, now.month

        last_year, last_month =get_before_year_month(year, month)
        # 嘗試撈取這個月和上個月的資料
        current_month_data, created_current = cls.objects.get_or_create(
            site=site, year=year, month=month,
            defaults={field: 0 for field in cls.get_field_names()}  # 初始化動態欄位
        )
        last_month_data, created_last = cls.objects.get_or_create(
            site=site, year=last_year, month=last_month,
            defaults={field: 0 for field in cls.get_field_names()}  # 同上
        )

        if created_current and created_last:
            # 如果這個月和上個月的資料都不存在，已經創建了空白資料
            return current_month_data

        if created_current and not created_last:
            # 如果這個月的資料不存在，但上個月的存在
            for field in cls.get_field_names():
                setattr(current_month_data, field, getattr(last_month_data, field))
            current_month_data.save()

        if not created_current and not created_last:
            # 如果這個月和上個月的資料都存在
            for field in cls.get_field_names():
                setattr(current_month_data, field, getattr(last_month_data, field))
            current_month_data.save()

        return current_month_data

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
    def get_current_by_query(cls, query,final_query=None, is_done=False):
        if final_query is None:
            final_query = Q()  # 初始化为一个空的 Q 对象
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

        final_query &= Q(id__in=ids) & Q(is_done=is_done)


        return (
            cls.objects.select_related("siteinfo")
            .filter(final_query)
            .order_by("siteinfo__genre","siteinfo__code")
            .all()
        )


    @classmethod
    def update_column_value_by_before(cls, site: SiteInfo,year:int,month:int, is_add: bool, column: str, value: Decimal):
        now = cls.get_current_by_site(site,year, month)
        b_year,b_month=get_before_year_month(year, month)
        before = cls.get_current_by_site(site,b_year,b_month)
        update_value =Decimal( getattr(before,column,0) )
        update_value += value if is_add else -value
        setattr(now,column,update_value)
        now.save()
        return now

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
