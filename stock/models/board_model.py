from decimal import Decimal

from django.db import models
from django.db.models import F, Q


from stock.models.material_model import Materials
from stock.models.monthreport_model import MonthReport
from stock.models.site_model import SiteInfo
from decimal import ROUND_HALF_UP
import logging

# # Create your models here.
import logging.config
from django.conf import settings

logging.config.dictConfig(settings.LOGGING)

logger = logging.getLogger(__name__)
static_column_code = {
    "21": "鋪路鐵板 全",
    "2105": "鋪路鐵板 半",
    "11": "簍空覆工板",
    "12": "洗車板",
}


class BoardReport(MonthReport):

    is_lost =models.BooleanField(default=False,verbose_name="是否遺失")

    mat_code = models.CharField(
        max_length=5, default="21", verbose_name="物料(預設鐵板 全)"
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
        mat_code = "21" if mat.mat_code in ["21", "2105"] else mat.mat_code
        mat_code2 = "2105" if mat.mat_code in ["21", "2105"] else None

        # 使用 get_or_create 方法简化对象获取或创建逻辑
        obj, _ = cls.objects.get_or_create(
            siteinfo=site, mat_code=mat_code, defaults={"mat_code2": mat_code2}
        )
        return obj

    @classmethod
    def add_report(
        cls,
        site: SiteInfo,
        remark: str,
        is_in: bool,
        mat: Materials,
        all_quantity: Decimal,
    ):
        if mat.mat_code not in static_column_code.keys() or (
            mat.mat_code == "11" and "簍空" not in remark
        ):
            return

        report = cls.get_board_report(site, mat)
        whse = cls.get_board_report(SiteInfo.objects.get(code="0001"), mat)
        code_str = "quantity2" if mat.mat_code == "2105" else "quantity"

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
