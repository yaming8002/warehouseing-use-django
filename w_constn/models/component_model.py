from django.db import models

from w_stock.models.material_model import Materials
from w_stock.models.site_model import SiteInfo


class TransComponent(models.Model):
    trans_code = models.CharField(max_length=10, verbose_name="進出單代碼")  # 交易代码
    build_date = models.DateField(verbose_name="Build Date")  # 建立日期
    constn_site = models.ForeignKey(
        SiteInfo,
        related_name="transport_site",
        on_delete=models.CASCADE,
        verbose_name="工地",
    )
    transaction_type = models.CharField(
        max_length=5, verbose_name="Transaction Type"
    )  # 交易类型 ('IN', 'OUT')
    turn_site = models.ForeignKey(
        SiteInfo,
        null=True,
        related_name="transport_trun_site",
        on_delete=models.CASCADE,
        verbose_name="轉單",
    )
    material = models.ForeignKey(
        Materials, on_delete=models.CASCADE, verbose_name="物料"
    )
    level = models.IntegerField(default=0, null=True, verbose_name="施工層別")
    remark = models.CharField(
        max_length=250, default="", null=True, verbose_name="備註"
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="數量"
    )
    unit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, verbose_name="單位量"
    )
    check = models.BooleanField(default=False, verbose_name="Check Status")  # 检查状态
    type = models.IntegerField(
        verbose_name="Transaction Type"
    )  # 交易类型（你可以根据需要定义不同类型的值）

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["build_date"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name} ({self.transaction_type})"
