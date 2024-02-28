from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from stock.models.site import SiteInfo
from stock.models.stock import ConStock, MainStock, StockBase

from trans.models import TransportDetailLog, TransportLog
from stock.models.material import Materials



@receiver(post_save, sender=TransportDetailLog)
def stock_post_save_receiver(sender, instance, created, **kwargs):
    if created:
        # 这里执行的操作将在新的 MyModel 实例被创建时触发
        translog = instance.transportlog
        # translog = TransportLog.objects.get(id =translog_id)
        mat = instance.material
        # print(mat.id,mat.name,mat.specification)
        stock_obj= MainStock.objects.filter(siteinfo=translog.form_site)
        con_stock_obj = ConStock.objects.filter(siteinfo=translog.to_site,material=mat)
        # print(str(stock_obj.filter(material=mat).all().query))
        stock = stock_obj.get(material=mat) # 預設倉庫裡應該都有對應的資料，暫且不管數量
        if con_stock_obj.count() > 0 :
            constock = con_stock_obj.first()
        else: 
            constock = con_stock_obj.create(
                siteinfo=translog.to_site,
                material=mat,
            )

        if "IN" in translog.transaction_type :
            chang_quantity_util(True, stock, instance.quantity,instance.unit)
            chang_quantity_util(False, constock, instance.quantity,instance.unit)
        else:
            chang_quantity_util(False, stock, instance.quantity,instance.unit)
            chang_quantity_util(True, constock, instance.quantity,instance.unit)
        stock.save()
        constock.save() 
        instance.save()
        pass
    else:
        # 这里执行的操作将在现有的 MyModel 实例被更新时触发
        pass


    
def chang_quantity_util(isadd: bool, whse: StockBase, quantity: Decimal, unit: Decimal):
    """
    Args:
        isadd (bool): _description_
        whse (Stock): _description_
        quantity (_type_): _description_
        unit (_type_): _description_
        用於調控數量與次級單位的計算
    """
    if isadd:
        whse.quantity += quantity
        whse.total_unit += unit * quantity
        whse.unit = unit 

    else:
        whse.quantity -= quantity
        if unit !=0 :
            whse.total_unit -= unit * quantity
            whse.unit = unit 