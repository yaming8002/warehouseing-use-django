from django.db import models

from w_stock.models.material_model import Materials
from w_trans.models.trans_model import TransLog


class LevelData(models.Model):
    translog = models.ForeignKey(
        TransLog,
        on_delete=models.CASCADE,
        verbose_name="進出料單",
    )
    html_name = models.CharField(max_length=100, verbose_name="名稱")

    level = models.IntegerField(default=0, null=True, verbose_name="施工層別")

    material = models.ForeignKey(
        Materials, on_delete=models.CASCADE, verbose_name="物料"
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="數量"
    )
    unit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, verbose_name="單位量"
    )
    remark = models.CharField(
        max_length=250, default=None, null=True, verbose_name="備註"
    )
    is_mid = models.BooleanField(default=False, verbose_name="檢查")

    class Meta:
        unique_together = (
            "translog",
            "material",
            "remark",
            "level"
        )
        abstract = True  # 確保這個類不會創建數據表


# 繼承 LevelData 並建立具體的表
class LevelBrace(LevelData):
    pass


class LevelComponent(LevelData):
    pass


class LevelTool(LevelData):
    pass
