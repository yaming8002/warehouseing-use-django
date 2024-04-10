from datetime import datetime
from django.db.models.signals import pre_save
from django.dispatch import receiver
from report.models import RailReport, SteelReport
from report.models.steel_model import DoneSteelReport
from stock.models.stock import ConStock
# 其他导入...

@receiver(pre_save, sender=ConStock)
def stock_pre_save_receiver(sender, instance, **kwargs):
    site = instance.siteinfo
    mat = instance.material

    if site.genre < 2 and instance.quantity > 0:
        return  # 如果条件满足，则不执行后续操作

    if mat.code in SteelReport.static_column_code.keys() and instance.quantity < 0:
        now = datetime.now()
        y, m = now.year, now.month
        DoneSteelReport.objects.create(
                siteinfo=site,
                done_type = 2,
                year=y,
                month=m,
                is_done=True,
        )

        instance.quantity = 0