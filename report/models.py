# from datetime import datetime
# from decimal import Decimal

# from django.db import models, transaction
# from django.db.models import F

# from stock.models.material import Materials
# from stock.models.site import SiteInfo
# from trans.models import TransLog, TransLogDetail
# from wcommon.templatetags import done_type_map
# # # Create your models here.


# class MonthReport(models.Model):
#     siteinfo = models.ForeignKey(
#         SiteInfo,
#         on_delete=models.SET_NULL,
#         null=True,
#         default=None,
#         verbose_name="地點",
#     )
#     edit_date = models.DateTimeField(default=datetime.now)
#     year = models.IntegerField(default=2010, verbose_name="年")
#     month = models.IntegerField(default=1, verbose_name="月份")
#     done_type = models.IntegerField(default=2, choices=done_type_map)
#     remark = models.TextField(null=True, verbose_name="說明")
#     is_done = models.BooleanField(default=False, verbose_name="結案")

#     @classmethod
#     def get_current_by_site(cls, site: SiteInfo):
#         report = cls.objects.filter(siteinfo=site).order_by("-year", "-month").first()
#         now = datetime.now()
#         year, month = now.year, now.month

#         if report is None:
#             report = cls.objects.create(
#                 siteinfo=site,
#                 year=year,
#                 month=month,
#             )

#         if report.year + report.month < year + month:
#             report.pk = None  # 将主键设为 None 以创建新对象
#             report.year = year
#             report.month = month

#         return report

#     class Meta:
#         unique_together = ("siteinfo", "year", "month", "done_type", "is_done")
#         abstract = True
#         ordering = ["id" ]  # 按照 id 升序排序


# class RailReport(MonthReport):

#     for i in range(5, 17):
#         locals()[f"in_{i}"] = models.IntegerField(default=0, verbose_name=f"In_{i}")
#         locals()[f"out_{i}"] = models.IntegerField(default=0, verbose_name=f"Out_{i}")
#     in_total = models.IntegerField(default=0, verbose_name="入庫總計")
#     out_total = models.IntegerField(default=0, verbose_name="出庫總計")
#     rail_ng = models.IntegerField(default=0, verbose_name="廢鐵")


#     @classmethod
#     def add_report(
#         cls, site: SiteInfo, is_in: bool, mat: Materials, all_quantity: Decimal ,all_unit:Decimal
#     ):
#         if mat.mat_code != "3050":
#             return False
#             # 获取当前年份和月份

#         # 使用事务确保操作的原子性
#         with transaction.atomic():
#             # 查找或创建针对特定工地的报告记录
#             report = cls.get_current_by_site(site)
#             whse = cls.get_current_by_site(SiteInfo.get_warehouse())

#             index = mat.specification.id  # 假设这里返回的值在5到16之间
#             if not 5 <= index <= 16:
#                 # 如果索引超出预期范围，可以在这里处理错误或忽略操作
#                 return False

#             in_field_name = f"in_{index}"
#             out_field_name = f"out_{index}"

#             # 根据是入库还是出库操作来更新相应的字段
#             if is_in:
#                 cls.objects.filter(id=report.id).update(**{
#                     in_field_name: F(in_field_name) + all_quantity,
#                     'in_total': F('in_total') + all_quantity,
#                 })
#                 cls.objects.filter(id=whse.id).update(**{
#                     in_field_name: F(in_field_name) + all_quantity,
#                     'in_total': F('in_total') + all_quantity,
#                 })
#             else:
#                 cls.objects.filter(id=report.id).update(**{
#                     out_field_name: F(out_field_name) + all_quantity,
#                     'out_total': F('out_total') + all_quantity,
#                 })
#                 cls.objects.filter(id=whse.id).update(**{
#                     in_field_name: F(in_field_name) - all_quantity,
#                     'in_total': F('in_total') - all_quantity,
#                 })


#         return True  # 假设操作成功时返回 True




# class SteelReport(MonthReport):

#     static_column_code = {
#         "300": "H300*300",
#         "301": "H300中柱",
#         "350": "H350*350",
#         "351": "H350中柱",
#         "390": "H390*400",
#         "400": "H400*400",
#         "401": "H400中柱",
#         "408": "H408*400",
#         "414": "H414*405",
#         "4141": "H414中柱",
#         "11": "覆工板 1M *2M",
#         "84": "覆工板 1M *3M",
#         "88": "水泥覆工板",
#         "13": "千斤頂",
#         "14": "土壓計",
#     }

#     for k, v in static_column_code.items():
#         locals()[f"m_{k}"] = models.DecimalField(
#             max_digits=10, decimal_places=2, default=0, verbose_name=v
#         )


#     @classmethod
#     def add_report(
#         cls, site: SiteInfo, is_in: bool, mat: Materials, all_quantity: Decimal,all_unit:Decimal
#     ):
#         if mat.mat_code not in cls.static_column_code.keys():
#             return False

#         # 使用事务确保操作的原子性
#         with transaction.atomic():
#             # 查找或创建针对特定工地的报告记录
#             report = cls.get_current_by_site(site)
#             whse = cls.get_current_by_site(SiteInfo.get_warehouse())
#             field_name = f"m_{mat.mat_code}"
#             # 根据是入库还是出库操作来更新相应的字段
#         value = all_unit if mat.is_divisible else all_quantity
#         if is_in:
#             # 对于入库操作，增加相应字段的值
#             cls.objects.filter(pk=report.pk).update(**{
#                 field_name: F(field_name) - value,
#             })
#             cls.objects.filter(pk=whse.pk).update(**{
#                 field_name: F(field_name) + value,
#             })
#         else:
#             cls.objects.filter(pk=report.pk).update(**{
#                 field_name: F(field_name) + value,
#             })
#             cls.objects.filter(pk=whse.pk).update(**{
#                 field_name: F(field_name) - value,
#             })


#         return True  # 假设操作成功时返回 True


# class StockMaterialSummary(models.Model):
#     steel = models.ForeignKey(
#         SteelReport, on_delete=models.CASCADE, verbose_name="項目"
#     )

#     year = models.IntegerField(default=2010, verbose_name="年")
#     month = models.IntegerField(default=1, verbose_name="月份")

#     material = models.ForeignKey(
#         Materials, on_delete=models.CASCADE, verbose_name="物料"
#     )

#     all_quantity = models.IntegerField(default=0, verbose_name="總數量")

#     class Meta:
#         unique_together = ["steel", "material", "all_quantity"]
#         ordering = ["id"]  # 按照 id 升序排序
