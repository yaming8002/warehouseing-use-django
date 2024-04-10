from decimal import Decimal
from django.db import models
from stock.models.material import Materials
from stock.models.site import SiteInfo


class StockBase(models.Model):
    siteinfo = models.ForeignKey(
        SiteInfo, on_delete=models.CASCADE, verbose_name="倉庫"
    )
    material = models.ForeignKey(
        Materials, on_delete=models.CASCADE, verbose_name="物料編號"
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="數量"
    )
    unit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="單位量"
    )
    total_unit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="總單位量"
    )

    @classmethod
    def getItem(cls, site: SiteInfo, mat: Materials):
        stock, _ = cls.objects.get_or_create(siteinfo=site, material=mat)
        return stock

    def change_quantity_util(self, is_add=True, quantity=Decimal(0), unit=Decimal(0)):
        if is_add:
            self.quantity += quantity
            self.total_unit += unit * quantity
        else:
            self.quantity -= quantity
            if unit != 0:
                self.total_unit -= unit * quantity
        self.unit = unit if unit != 0 else self.unit
        self.save()

    class Meta:
        unique_together = ["siteinfo", "material"]
        abstract = True
        ordering = ["siteinfo", "material"]  # 按照 id 升序排序


class MainStock(StockBase):
    date_tag = models.DateField(null=True, verbose_name="時間標籤")

    @classmethod
    def move_material(cls, site, mat, quantity, unit, is_in=True):
        stock = cls.getItem(SiteInfo.get_warehouse(), mat)
        stock.change_quantity_util(is_in, quantity, unit)

    class Meta:
        verbose_name = "主庫存"
        verbose_name_plural = "主庫存"


class ConStock(StockBase):
    @classmethod
    def move_material(cls, site, mat, quantity, unit, is_in=True):
        stock = cls.getItem(site, mat)
        stock.change_quantity_util(is_in, quantity, unit)

    class Meta:
        verbose_name = "建設庫存"
        verbose_name_plural = "建設庫存"
