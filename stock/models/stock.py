from django.db import models
from stock.models.material import Materials
from stock.models.site import SiteInfo

class StockBase(models.Model):
    siteinfo =  models.ForeignKey(SiteInfo, on_delete=models.CASCADE, verbose_name="倉庫")
    material = models.ForeignKey(Materials, on_delete=models.CASCADE, verbose_name="物料編號")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="數量")
    unit = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="單位量")
    total_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="總單位量")

    class Meta:
        unique_together = ("siteinfo", "material")
        abstract = True
        ordering = ['siteinfo','material']  # 按照 id 升序排序


class MainStock(StockBase):
    class Meta:
        verbose_name = "主庫存"
        verbose_name_plural = "主庫存"


class ConStock(StockBase):
    class Meta:
        verbose_name = "建設庫存"
        verbose_name_plural = "建設庫存"