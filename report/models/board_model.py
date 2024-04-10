from datetime import datetime
from decimal import Decimal

from django.db import models, transaction
from django.db.models import F, Q
from django.utils.timezone import datetime

from report.models.monthreport_model import MonthData, MonthReport
from stock.models.material import Materials
from stock.models.site import SiteInfo
from stock.models.stock import MainStock
from trans.models import TransLog
from trans.models.trans import TransLogDetail
from wcommon.utils.uitls import excel_value_to_str, get_year_month
from decimal import ROUND_HALF_UP
import logging
# # Create your models here.
import logging.config
from django.conf import settings

logging.config.dictConfig(settings.LOGGING)

logger = logging.getLogger(__name__)
static_column_code = {
    "21":"鋪路鐵板 全",
    "2105":"鋪路鐵板 半",
    "11":"簍空覆工板",
    "12": "洗車板",
}

class BoardReport(MonthReport):

    mat_code = models.CharField(max_length=5, default="21", verbose_name="物料(預設鐵板 全)")
    mat_code2 = models.CharField(max_length=5, default="2105",null=True, verbose_name="物料(預設鐵板半)")

    quantity =models.DecimalField(
            max_digits=10, decimal_places=2, default=0, verbose_name="數量"
        )
    
    quantity2 =models.DecimalField(
            max_digits=10, decimal_places=2, default=0, verbose_name="數量2"
        )

    close=models.BooleanField(default=False,null=True,verbose_name="關閉")

    @classmethod
    def add_report(
        cls,
        detail: TransLogDetail,
        is_in: bool,
        mat: Materials,
        all_quantity: Decimal,
    ):
        if mat.mat_code not in static_column_code.keys() or \
            (mat.mat_code == '11' and "簍空" not in detail.remark ) :
            return 
        
        site= detail.translog.constn_site
        report = cls.get_current_by_site(site=site)
        whse = cls.get_current_by_site(site=SiteInfo.objects.get(code='0001'))
        value =  all_quantity
        code_str = "quantity2"  if mat.mat_code == '2105' else "quantity"
        float_value = getattr(report, code_str)
        if isinstance(float_value, float):
            float_value = Decimal(str(float_value))

        if is_in:
            setattr(report,code_str,report.get_column_decimal_val(code_str)-value )
            setattr(whse,code_str,whse.get_column_decimal_val(code_str)+value )
        else:
            setattr(report,code_str,report.get_column_decimal_val(code_str)+value )
            setattr(whse,code_str,whse.get_column_decimal_val(code_str)-value )
        # logger.info(model_to_dict(report))
        whse.update_edit_date()
        report.update_edit_date()
        whse.save()
        report.save() 

    class Meta:
        unique_together = ("siteinfo", "year", "month", "done_type", "is_done","mat_code")
