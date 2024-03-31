
from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from datetime import datetime
from django.db.models import Q
from stock.models.material import Materials
from stock.models.site import SiteInfo
from trans.models.car import CarInfo
from wcommon.utils.uitls import excel_num_to_date, excel_value_to_str, get_month_range


class TransLog(models.Model):
    code = models.CharField(max_length=20)
    constn_site = models.ForeignKey(
        SiteInfo,
        related_name="transport_site",
        on_delete=models.CASCADE,
        verbose_name="工地",
    )
    turn_site = models.ForeignKey(
        SiteInfo,
        null=True,
        related_name="transport_trun_site",
        on_delete=models.CASCADE,
        verbose_name="轉單",
    )
    build_date = models.DateTimeField(default=datetime.now)
    carinfo = models.ForeignKey(
        CarInfo, null=True, on_delete=models.CASCADE, verbose_name="車輛"
    )

    transaction_type = models.CharField(
        max_length=3, choices=[("IN", "入料"), ("OUT", "出料")]
    )

    member = models.CharField(max_length=20, null=True, verbose_name="經手人")

    @classmethod
    def create(cls, code: str, item: list):

        consite = excel_value_to_str(item[2], 4)
        turn_site = excel_value_to_str(item[3], 4)

        consite = SiteInfo.objects.get(code=consite)
        if turn_site is not None:
            turn_site = SiteInfo.objects.get(code=turn_site)

        transaction_type = "IN" if item[15] is not None and item[15] > 0 else "OUT"

        build_date = excel_num_to_date(item[1])

        if build_date is None:
            build_date = datetime.now()
        build_date_range = get_month_range(build_date)
        query = (
            Q(code=code)
            & Q(constn_site=consite)
            & Q(build_date__gte=build_date_range[0])
            & Q(build_date__lte=build_date_range[1])
            & Q(transaction_type=transaction_type)
        )
        # print(cls.objects.filter(query).query)
        if cls.objects.filter(query).exists():
            return cls.objects.get(query)

        car_firm = excel_value_to_str(item[23])
        car_number = excel_value_to_str(item[24])

        carinfo = CarInfo.create(car_number=car_number, firm=car_firm)
        member = excel_value_to_str(item[26])

        return cls.objects.create(
            code=code,
            constn_site=consite,
            turn_site=turn_site,
            carinfo=carinfo,
            transaction_type=transaction_type,
            member=member,
            build_date=build_date,
        )

    class Meta:
        unique_together = [
            "code",
            "constn_site",
            "carinfo",
            "transaction_type",
            "turn_site",
            "build_date",
        ]

class TransLogDetail(models.Model):
    translog = models.ForeignKey(
        TransLog,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )
    material = models.ForeignKey(
        Materials, on_delete=models.CASCADE, verbose_name="物料"
    )
    
    is_rent = models.BooleanField(default=False, verbose_name="租賃")
    level = models.IntegerField(default=0, null=True, verbose_name="施工層別")
    rollback = models.BooleanField(default=False, verbose_name="作廢")
    quantity = models.IntegerField(default=0, verbose_name="數量")
    all_quantity = models.IntegerField(default=0, verbose_name="總數量")
    unit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, verbose_name="單位量"
    )
    all_unit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, verbose_name="總單位量"
    )
    remark = models.TextField(default="", null=True, verbose_name="備註")

    @classmethod
    def create(cls, tran: TransLog, item: list, is_rent: False):
        unit_req = item[9]
        # print(type(unit_req))

        unit = Decimal("{:.2f}".format(unit_req)) if unit_req else None
        quantity = Decimal(abs(item[15]))
        mat_code = excel_value_to_str(item[7])
        level = int(item[21]) % 10 if item[21] else None
        remark = str(item[20])
        mat = Materials.get_item_by_code(mat_code, remark, unit)

        all_unit = unit * quantity if unit else Decimal(0)
        cls.objects.get_or_create(
            translog=tran,
            material=mat,
            is_rent=is_rent,
            level=level,
            quantity=quantity,
            all_quantity=quantity,
            unit=unit,
            all_unit=all_unit,
            remark=remark,
        )

    @classmethod
    def rollback(cls, tran):
        detials = (
            cls.objects.select_related("translog").filter(translog__code=tran).all()
        )
        for detial in detials:
            detial.rollback = True
            detial.save()

    class Meta:
        unique_together = ["translog", "material", "level", "unit", "remark"]
