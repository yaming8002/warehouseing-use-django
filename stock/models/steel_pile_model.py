
from django.db import models

from stock.models.material_model import Materials
from trans.models.trans_model import TransLog

# # Create your models here.


class SteelPile(models.Model):
    translog = models.ForeignKey(
        TransLog,
        related_name="transport_site",
        on_delete=models.CASCADE,
        verbose_name="工地",
    )

    material = models.ForeignKey(
        Materials, on_delete=models.CASCADE, verbose_name="物料"
    )

    is_mid = models.BooleanField(default=False, verbose_name="是構台梁")
    is_ng = models.BooleanField(default=False, verbose_name="是NG")

    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="數量"
    )

    unit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, verbose_name="單位量"
    )

    remark = models.CharField(
        max_length=250, default=None, null=True, verbose_name="備註"
    )


    class Meta:
        unique_together = [
            "translog",
            "material",
            "is_mid",
            "is_ng",
            'remark'
        ]
