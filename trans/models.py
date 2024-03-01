from decimal import Decimal
from django.db import models
from datetime import datetime

from stock.models.material import Materials
from stock.models.site import SiteInfo


# Create your models here.
class CarInfo(models.Model):
    car_number = models.CharField( max_length=15,  verbose_name="車牌")
    firm = models.CharField(max_length=30, default='',  verbose_name="公司")
    is_not_count = models.BooleanField(default=False, verbose_name="非報價")
    value=models.DecimalField(max_digits=10,default=0, decimal_places=2,verbose_name="基本台金額",null=True)
    remark = models.TextField( verbose_name="噸數(備註)",default='', null=True)


    @classmethod
    def create(cls, car_number, firm=None, remark=None, value=None ,is_not_count=False ):
        firm = '' if firm is None else firm
        is_not_count = firm == ''
        value = Decimal(value) if value else Decimal(0)
        return cls.objects.create(car_number=car_number, firm=firm, remark=remark,value=value,is_not_count=is_not_count)

    class Meta:
        unique_together = ["car_number","firm"]
        ordering = ["firm","car_number"]  # 按照 id 升序排序
    
    def __str__(self):
        return f"{self.car_number} 公司:{self.firm} "
    
    

class TransportLog(models.Model):
    code = models.CharField(max_length=20)
    form_site = models.ForeignKey(SiteInfo,on_delete=models.CASCADE, related_name='transport_whse' ,verbose_name="來源地")
    to_site = models.ForeignKey(SiteInfo, related_name='transport_constn', on_delete=models.CASCADE, verbose_name="目的地")
    turn_site = models.ForeignKey(SiteInfo, null=True, related_name='transport_trun_constn', on_delete=models.CASCADE, verbose_name="轉單")
    build_date = models.DateTimeField(default=datetime.now)
    carinfo = models.ForeignKey(CarInfo, on_delete=models.CASCADE, verbose_name="車輛" )
    transaction_type = models.CharField(max_length=3, choices=[('IN', '入料'), ('OUT', '出料')])

    member = models.CharField(max_length=20,verbose_name="經手人")
    
    class Meta:
        unique_together = [ 'code', 'form_site','to_site', 'turn_site','build_date', 'carinfo','transaction_type']
    
class TransportDetailLog(models.Model):
    transportlog = models.ForeignKey(TransportLog, on_delete=models.CASCADE, verbose_name="運輸")
    material = models.ForeignKey(Materials, on_delete=models.CASCADE, verbose_name="物料")
    level = models.IntegerField(default=0,null=True,verbose_name="施工層別" )
    quantity = models.IntegerField(default=0, verbose_name="數量")
    all_quantity = models.IntegerField(default=0, verbose_name="總數量")
    unit = models.DecimalField(max_digits=10, decimal_places=2, default=0 , null=True ,verbose_name="單位量" )
    all_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True, verbose_name="總單位量")
    remark = models.TextField(default='', null=True,verbose_name="備註")

    class Meta:
        unique_together = ['transportlog', 'material','level','unit','remark']
        ordering = ['id']  # 按照 id 升序排序
