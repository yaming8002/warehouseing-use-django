from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from constn.models import ConStock, Construction
from trans.models import TransportDetailLog, TransportLog
from whse.models.material import Materials
from whse.models.whse import Stock, StockBase, WhseList


@receiver(post_save, sender=TransportDetailLog)
def stock_post_save_receiver(sender, instance, created, **kwargs):
    if created:
        # 这里执行的操作将在新的 MyModel 实例被创建时触发
        translog = instance.logistics
        # translog = TransportLog.objects.get(id =translog_id)
        constn = Construction.objects.get(code= translog.construction)
        mat = instance.material
        stock_obj= Stock.objects.filter(whse=translog.whse)
        con_stock_obj = ConStock.objects.filter(construction=translog.construction,materiel=mat)

        stock = stock_obj.get(materiel=mat) # 預設倉庫裡應該都有對應的資料，暫且不管數量
        if con_stock_obj.count() > 0 :
            constock = con_stock_obj.first()
        else: 
            constock = con_stock_obj.create(
                construction=constn,
                materiel=mat,
            )

        if "入" in translog.transaction_type :
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