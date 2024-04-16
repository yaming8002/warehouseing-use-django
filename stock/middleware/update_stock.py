# from datetime import datetime
# from django.db.models.signals import pre_save
# from django.dispatch import receiver
# from django.forms import model_to_dict
# from report.models import RailReport, SteelReport
# from report.models.steel_model import DoneSteelReport
# from stock.models.site import SiteInfo
# from stock.models.stock import ConStock
# # 其他导入...

# @receiver(pre_save, sender=ConStock)
# def stock_pre_save_receiver(sender, instance, **kwargs):
#     site = instance.siteinfo
#     mat = instance.material
#     if site.genre < 2 or instance.quantity > 0:
#         return  # 如果条件满足，则不执行后续操作
    

#     if mat.mat_code in SteelReport.static_column_code.keys() and instance.quantity < 0:
#         print("dddddddddddd")
#         now = datetime.now()
#         y, m = now.year, now.month
#         total = SteelReport.get_current_by_site(SiteInfo.objects.get(code="0000"), y, m)
#         check_done = DoneSteelReport.objects.gercreate(
#                 siteinfo=site,
#                 done_type = 2,
#                 year=y,
#                 month=m,
#                 is_done=True,
#         )
#         print("check_done",model_to_dict(check_done))
#         value = instance.total_unit if instance.total_unit else instance.quantity
#         total = SteelReport.get_current_by_site(SiteInfo.objects.get(code="0000"), y, m)
#         print("total",model_to_dict(total))
#         SteelReport.update_column_value(total.id,True,f"m_{mat.mat_code}",value)
#         instance.quantity = 0