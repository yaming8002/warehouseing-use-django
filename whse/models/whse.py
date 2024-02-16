from django.db import models

from .material import MatList


class WhseList(models.Model):
    name = models.CharField(max_length=30, verbose_name="倉庫名稱")
    address = models.TextField(verbose_name="地址")


class StockBase(models.Model):
    materiel = models.ForeignKey(
        MatList,primary_key=True, on_delete=models.CASCADE, verbose_name="物料編號"
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="數量"
    )
    unit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="單位量"
    )

    class Meta:
        abstract = True


class Stock(StockBase):
    whse = models.ForeignKey(WhseList, on_delete=models.CASCADE, verbose_name="倉庫")

    class Meta:
        unique_together = ("whse", "materiel")
