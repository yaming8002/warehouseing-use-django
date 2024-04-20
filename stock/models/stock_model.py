from datetime import datetime
from decimal import Decimal
from django.db import models
from django.forms import model_to_dict

from stock.models.material_model import Materials
from stock.models.site_model import SiteInfo
from django.db.models import Q

from stock.models.steel_model import DoneSteelReport, SteelReport

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
        try:
            stock, created = cls.objects.get_or_create(
                siteinfo=site,
                material=mat
            )
            return stock
        except cls.MultipleObjectsReturned:
            stocks = cls.objects.filter(siteinfo=site, material=mat)
            # Handle the situation, e.g., by choosing the first one
            return stocks.first()
    
        
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
        unique_together = ('siteinfo', 'material')
        abstract = True
        ordering = ["siteinfo", "material"]  # 按照 id 升序排序


class MainStock(StockBase):
    date_tag = models.DateField(null=True, verbose_name="時間標籤")

    @classmethod
    def move_material(cls, mat, quantity, unit, is_in=True):
        stock = cls.getItem(SiteInfo.get_warehouse(), mat)
        stock.change_quantity_util(is_in, quantity, unit)
        stock.save()

    class Meta:
        unique_together = ["siteinfo", "material"]
        verbose_name = "主庫存"
        verbose_name_plural = "主庫存"


class ConStock(StockBase):


    @classmethod
    def move_material(cls, site, mat, quantity, unit, is_in=True):
        stock = cls.getItem(site, mat)
        stock.change_quantity_util(is_in, quantity, unit)
        if site.genre > 1 and stock.quantity < 0 and mat.mat_code in SteelReport.static_column_code.keys() :
            now = datetime.now()
            y, m = now.year, now.month
            check_done,_ = DoneSteelReport.objects.get_or_create(
                    siteinfo=site,
                    done_type = 2,
                    year=y,
                    month=m,
                    is_done=True,
            )
            value = quantity*unit if unit else stock.quantity
            DoneSteelReport.update_column_value(check_done.id, True, f"m_{mat.mat_code}", value)
            total = SteelReport.get_current_by_site(SiteInfo.objects.get(code="0000"), y, m)
            SteelReport.update_column_value(total.id,True,f"m_{mat.mat_code}",value)
            stock.quantity = 0
            stock.unit = 0
            stock.total_unit = 0

        stock.save()

    class Meta:
        unique_together = ["siteinfo", "material"]
        verbose_name = "建設庫存"
        verbose_name_plural = "建設庫存"
