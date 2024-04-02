from datetime import datetime
from decimal import Decimal

from django.db import models, transaction
from django.db.models import F
from django.db.models import Q
from stock.models.material import Materials
from stock.models.site import SiteInfo
from trans.models import TransLog, TransLogDetail
from wcommon.templatetags import done_type_map
from django.forms.models import model_to_dict
from typing import Optional
from django.db.models import Window, F
from django.db.models.functions import Rank
# # Create your models here.


class MonthData(models.Model):

    year = models.IntegerField(default=2010, verbose_name="年")
    month = models.IntegerField(default=1, verbose_name="月份")

    class Meta:
        unique_together = ("year", "month")
        abstract = True
        ordering = ["id" ]  # 按照 id 升序排序


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
    def get_current_by_site(cls, site: SiteInfo ,year: Optional[int] = None, month: Optional[int] = None):
        if year is None:
            now = datetime.now()
            year, month = now.year, now.month

        query_str = """
                    SELECT * FROM report_railreport
                    WHERE siteinfo_id = %s
                    AND (`year` < %s OR (`year` = %s AND `month` <= %s))
                    ORDER BY `year` DESC, `month` DESC
                    """
        
        reports = cls.objects.raw(query_str, [site.id, year, year, month])

        if reports:
            report = reports[0]
        else:
            report = cls.objects.create(
                siteinfo=site,
                year=year,
                month=month,
            )

        if f'{report.year}{report.month}' < f'{year}{month}' :
            report.pk = None  
            report.year = year
            report.month = month

        return report


    @classmethod
    def get_current_by_query(cls,query, is_done=False ):
        query_set = (
            cls.objects
            .annotate(
                rank=Window(
                    expression=Rank(),
                    partition_by=[F('siteinfo__id')],
                    order_by=[F('year').desc(), F('month').desc()]
                )
            )
            .filter(rank=1)
            .filter(query)
            .order_by('-year', '-month')
            .values('id', 'siteinfo__id')
        )

        ids = [item['id'] for item in query_set]
        return cls.objects.select_related('siteinfo').filter(id__in=ids).filter(is_done=is_done).all()
    
    def get_column_decimal_val(self, column:str):
        float_value = getattr(self, column)
        if isinstance(float_value, float):
            float_value = Decimal(str(float_value))
        return float_value

    class Meta:
        unique_together = ("siteinfo", "year", "month", "done_type", "is_done")
        abstract = True
        ordering = ["id" ]  # 按照 id 升序排序