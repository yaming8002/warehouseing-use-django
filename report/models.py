# from django.db import models
# from stock.views import materials

# from trans.models import TransportLog

# # Create your models here.

# class SteelPileReport(models.Model):
#     transportlog = models.ForeignKey(TransportLog, on_delete=models.CASCADE, verbose_name="運輸")
#     material = models.ForeignKey(materials, on_delete=models.CASCADE, verbose_name="物料")
#     level = models.IntegerField(default=0,null=True,verbose_name="施工層別" )
#     all_quantity = models.IntegerField(default=0, verbose_name="總數量")
#     all_unit = models.DecimalField(max_digits=10, decimal_places=2, default=-1,null=True, verbose_name="總單位量")
#     remark = models.TextField( null=True,verbose_name="備註")

#     class Meta:
#         unique_together = ['transportlog', 'material','level','unit','remark']
#         ordering = ['id']  # 按照 id 升序排序
