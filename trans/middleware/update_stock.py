from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from report.models import RailReport, SteelReport
from report.models.board_model import BoardReport
from report.models.steel_model import SteelPillar
from trans.models import TransLogDetail


@receiver(post_save, sender=TransLogDetail)
def stock_post_save_receiver(sender, instance, created, **kwargs):
    translog = instance.translog
    mat = instance.material
    quantity = instance.quantity if instance.quantity else Decimal(0)
    is_stock_add = translog.transaction_type == "IN"
    RailReport.add_report(translog, is_stock_add, mat, quantity)
    BoardReport.add_report(instance, is_stock_add, mat, quantity)
    all_unit = instance.all_unit if instance.all_unit else Decimal(0)
    SteelReport.add_report(translog, is_stock_add, mat, quantity, all_unit)

