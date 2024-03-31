from datetime import datetime
from threading import Thread

from django.db.models.signals import post_save
from django.dispatch import receiver

from report.models.steel_model import SteelPillar
from stock.models.stock import  MainStock


check_NG_list = ["鋼軌", "H300", "H350", "H400"]


@receiver(post_save, sender=MainStock)
def report_save_receiver(sender, instance, created, **kwargs):
    if created:
        t = Thread(target=report_post_save_work, args=(instance,))
        t.start()


def report_post_save_work(instance: MainStock):
    now = datetime.now()
    year,month = now.year,now.month 
    mat = MainStock.material
    SteelPillar.update_value(mat_code=mat.mat_code,year=year,month=month)
    