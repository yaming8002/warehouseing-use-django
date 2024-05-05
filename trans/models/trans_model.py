from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from datetime import datetime
from django.db.models import Q
from stock.models.board_model import BoardReport
from stock.models.material_model import Materials
from stock.models.rail_model import RailReport
from stock.models.site_model import SiteInfo
from stock.models.steel_model import DoneSteelReport, SteelReport
from stock.models.stock_model import ConStock, MainStock
from trans.models.car_model import CarInfo
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
    is_rollback = models.BooleanField(default=False, verbose_name="作廢")
    quantity = models.IntegerField(default=0, verbose_name="數量")
    all_quantity = models.IntegerField(default=0, verbose_name="總數量")
    unit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, verbose_name="單位量"
    )
    all_unit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, verbose_name="總單位量"
    )
    remark = models.CharField(
        max_length=250, default="", null=True, verbose_name="備註"
    )

    @classmethod
    def create(cls, tran: TransLog, item: list, is_rent: False):
        unit_req = item[9]

        unit = Decimal("{:.2f}".format(unit_req)) if unit_req else None
        quantity = Decimal(abs(item[15]))
        mat_code = excel_value_to_str(item[7])
        level = int(item[21]) % 10 if item[21] else None
        remark = str(item[20])
        mat = Materials.get_item_by_code(mat_code, remark, unit)

        all_unit = unit * quantity if unit else Decimal(0)
        obj, created = cls.objects.get_or_create(
            translog=tran,
            material=mat,
            level=level,
            unit=unit,
            is_rollback = False,
            defaults={
                'is_rent': is_rent,
                'quantity': quantity,
                'all_quantity': quantity,
                'all_unit': all_unit,
                'remark': remark,
            }
        )

        if not created:
            # 計算差異值
            diff_quantity = quantity - obj.quantity
            diff_all_unit = all_unit - obj.all_unit
            if  diff_quantity == 0 and diff_all_unit == 0:
                return 

            obj.quantity = quantity
            obj.all_quantity = quantity
            obj.all_unit = all_unit
            obj.remark = remark 
            quantity = diff_quantity
            all_unit = diff_all_unit
                # 保存更新
            obj.save(update_fields=['quantity', 'all_quantity', 'all_unit', 'remark'])


        is_stock_add = tran.transaction_type == "IN"
        MainStock.move_material(mat, quantity, all_unit, is_stock_add)

        if DoneSteelReport.add_new_mat( tran.constn_site, tran.turn_site, tran.build_date, is_stock_add, mat, quantity, all_unit ,remark ):
            """if this case not new material"""
            ConStock.move_material( tran.constn_site, mat, quantity, all_unit, not is_stock_add )
            SteelReport.add_report( tran.constn_site, tran.build_date, is_stock_add, mat, quantity, all_unit )
            
        RailReport.add_report( tran.constn_site, tran.build_date, is_stock_add, mat, quantity )
        BoardReport.add_report(tran.constn_site, remark, is_stock_add, mat, quantity)

    @classmethod
    def rollback(cls, tran , detial_id=None):
        if detial_id :
            detials = (
                cls.objects.select_related("translog").filter(id=detial_id).all()
            )
        else:
            detials = (
                cls.objects.select_related("translog").filter(translog=tran).all()
            )
        for detail in detials:
            cls.objects.select_related("translog").filter(translog__code=tran, material=detail.material).exclude(id=detail.id).delete()
            detail.is_rollback = True
            detail.save()
            is_stock_add = tran.transaction_type != "IN" # 回滾 反向 計算 
            mat = detail.material
            quantity = detail.quantity
            all_unit = detail.all_unit
            remark = detail.remark
            MainStock.move_material(mat, quantity, all_unit, is_stock_add)

            if DoneSteelReport.add_new_mat( tran.constn_site, tran.turn_site, tran.build_date, is_stock_add, mat, quantity, all_unit ,remark ):
                """if this case not new material"""
                ConStock.move_material( tran.constn_site, mat, quantity, all_unit, not is_stock_add )
                SteelReport.add_report( tran.constn_site, tran.build_date, is_stock_add, mat, quantity, all_unit )
                
            RailReport.add_report( tran.constn_site, tran.build_date, is_stock_add, mat, quantity )
            BoardReport.add_report(tran.constn_site, remark, is_stock_add, mat, quantity)


    class Meta:
        unique_together = ["translog", "material", "level","is_rollback", "unit", "remark"]
