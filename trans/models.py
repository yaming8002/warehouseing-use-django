from django.db import models

from constn.models import Construction
from whse.models.material import MatList
from whse.models.whse import WhseList


# Create your models here.
class CarInfo(models.Model):
    car_number = models.CharField( max_length=15,  verbose_name="車牌")
    driver =models.CharField( max_length=30,   verbose_name="駕駛人員" ,null=True)
    firm = models.CharField(max_length=30, verbose_name="公司")
    patload = models.CharField( max_length=30 , verbose_name="噸數",null=True)
    value=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="基本台金額",null=True)
    remark = models.TextField( verbose_name="備註",null=True)

    class Meta:
        unique_together = ["car_number"]
    
    def __str__(self):
        return f"{self.car_number} 公司:{self.firm} "
    

class TransportLog(models.Model):
    code = models.CharField(max_length=20)
    whse = models.ForeignKey(WhseList,on_delete=models.CASCADE, related_name='transport_main_whse' ,verbose_name="倉庫")
    construction = models.ForeignKey(Construction, related_name='transport_main_constn', on_delete=models.CASCADE, verbose_name="目的地")
    towhse = models.ForeignKey(WhseList,on_delete=models.CASCADE,related_name='transport_to_whse', verbose_name="轉單倉庫" , null=True)
    toconstruction = models.ForeignKey(Construction, related_name='transport_to_constn', on_delete=models.CASCADE, verbose_name="轉單來源地", null=True)
    build_date = models.DateTimeField(auto_now_add=True)
    car = models.ForeignKey(CarInfo, on_delete=models.CASCADE, verbose_name="來源地" )
    transaction_type = models.CharField(max_length=3, choices=[('IN', '入料'), ('OUT', '出料')])

    level = models.IntegerField(default=0)
    member = models.CharField(max_length=20)

    class Meta:
        unique_together = [ 'code', 'construction', 'build_date', 'car']
    
class TransportDetailLog(models.Model):
    logistics = models.ForeignKey(TransportLog, on_delete=models.CASCADE, verbose_name="運輸")
    material = models.ForeignKey(MatList, on_delete=models.CASCADE, verbose_name="物料")
    quantity = models.IntegerField(default=0, verbose_name="數量")
    all_quantity = models.IntegerField(default=0, verbose_name="總數量")
    unit = models.DecimalField(max_digits=10, decimal_places=2, default=-1 , null=True ,verbose_name="單位量" )
    all_unit = models.DecimalField(max_digits=10, decimal_places=2, default=-1,null=True, verbose_name="總單位量")
    remark = models.TextField( null=True,verbose_name="備註")

    class Meta:
        unique_together = ['logistics', 'material']
