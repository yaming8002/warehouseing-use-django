from datetime import datetime
from decimal import Decimal
from django.db import models
from django.forms import model_to_dict

from stock.models.material_model import Materials
from stock.models.site_model import SiteInfo
from django.db.models import Q



class Stock(models.Model):
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
    date_tag = models.DateField(null=True, verbose_name="時間標籤")

    @classmethod
    def getItem(cls, site: SiteInfo, mat: Materials):
        try:
            stock, _ = cls.objects.get_or_create(siteinfo=site, material=mat)
            return stock
        except cls.MultipleObjectsReturned:
            stocks = cls.objects.filter(siteinfo=site, material=mat)
            # Handle the situation, e.g., by choosing the first one
            return stocks.first()

    @classmethod
    def move_material(cls, site: SiteInfo, mat: Materials, quantity=Decimal(0), unit=Decimal(0), is_in=True):
        stock = cls.getItem(site, mat)
        stock.change_quantity_util(is_in, quantity, unit)
        stock.save()

    def change_quantity_util(self, is_add=True, quantity=Decimal(0), unit=Decimal(0)):
        if is_add:
            self.quantity += quantity
            self.total_unit += unit * quantity
        else:
            self.quantity -= quantity
            if unit != 0:
                self.total_unit -= unit * quantity
        self.unit = unit if unit != 0 else self.unit

    class Meta:
        unique_together = ["siteinfo", "material"]
        ordering = ["siteinfo", "material"]  # 按照 id 升序排序

