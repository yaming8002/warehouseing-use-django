from datetime import datetime
from decimal import Decimal
import sys

from django.db import models, transaction
from django.forms import model_to_dict

from stock.models.material_model import Materials
from stock.models.monthreport_model import MonthReport
from stock.models.site_model import SiteInfo
from stock.models.stock_model import Stock
from wcom.utils.uitls import get_year_month
import logging

# # Create your models here.
import logging.config
from django.conf import settings

logging.config.dictConfig(settings.LOGGING)

logger = logging.getLogger(__name__)


class SteelReport(MonthReport):
    static_column_code = {
        "300": "H300*300",
        "301": "H300中柱",
        "350": "H350*350",
        "351": "H350中柱",
        "390": "H390*400",
        "400": "H400*400",
        "401": "H400中柱",
        "408": "H408*400",
        "414": "H414*405",
        "4141": "H414中柱",
        "92": "覆工板",
        "12": "千斤頂",
        "13": "土壓計",
    }

    for k, v in static_column_code.items():
        locals()[f"m_{k}"] = models.DecimalField(
            max_digits=10, decimal_places=2, default=0.0, verbose_name=v
        )

    @classmethod
    def add_report(
        cls,
        site: SiteInfo,
        build_date: datetime,
        is_in: bool,
        mat: Materials,
        all_quantity: Decimal,
        all_unit: Decimal,
    ):
        if mat.mat_code not in cls.static_column_code.keys():
            return
        if site.code=="1542":
            print("".join(["=====" for x in range(30)]))
            print(model_to_dict(mat))
            sys.exit(0)
        year, month = build_date.year, build_date.month
        report = cls.get_current_by_site(site, year, month)
        whse = cls.get_current_by_site(SiteInfo.objects.get(code="0001"), year, month)

        value = all_unit if mat.is_divisible else all_quantity
        value = Decimal(value)
        cls.update_column_value(whse.id, not is_in, f"m_{mat.mat_code}", value)
        cls.update_column_value(report.id, not is_in, f"m_{mat.mat_code}", value)


class DoneSteelReport(MonthReport):
    static_column_code = {
        "300": "H300*300",
        "301": "H300中柱",
        "350": "H350*350",
        "351": "H350中柱",
        "390": "H390*400",
        "400": "H400*400",
        "401": "H400中柱",
        "408": "H408*400",
        "414": "H414*405",
        "4141": "H414中柱",
        "92": "覆工板",
        "12": "千斤頂",
        "13": "土壓計",
    }

    turn_site = models.ForeignKey(
        SiteInfo,
        null=True,
        related_name="steel_trun_site",
        on_delete=models.CASCADE,
        verbose_name="轉單",
    )

    for k, v in static_column_code.items():
        locals()[f"m_{k}"] = models.DecimalField(
            max_digits=10, decimal_places=2, default=0.0, null=True, verbose_name=v
        )

    class Meta:
        unique_together = ("siteinfo","turn_site", "year", "month", "done_type", "is_done")
        verbose_name = "變動資訊"
        verbose_name_plural = "變動資訊"
        ordering = ["done_type", "id"]  # 按照 id 升序排序

    @classmethod
    def add_new_mat(
        cls,
        site: SiteInfo,
        turn_site: SiteInfo,
        build_date: datetime,
        is_in: bool,
        mat: Materials,
        all_quantity: Decimal,
        all_unit: Decimal,
        remark:str
    ):
        y, m = build_date.year, build_date.month
        if  site.genre ==1 or not is_in or mat.mat_code not in cls.static_column_code.keys() :
            return True

        report, _ = cls.objects.get_or_create(
            siteinfo=site,
            turn_site=turn_site,
            year=y,
            month=m,
            done_type=2,
            is_done=True
        )
        
        value = all_unit if mat.is_divisible else all_quantity
        value = Decimal(value)
        cls.update_column_value(report.id, True, f"m_{mat.mat_code}", value)
        # SteelReport = cls.get_current_by_site(SiteInfo.objects.get(code="0001"), y, m)
        # print(model_to_dict(cls.objects.get(id=report.id)))
        return False

    @classmethod
    def roll_back(
        cls,
        site: SiteInfo
    ):
        cls.objects.filter(siteinfo=site).update(**{"is_done":False})
        report = SteelReport.get_current_by_site(site)
        report.is_done = True
        total = SteelReport.get_current_by_site(SiteInfo.objects.get(code="0000"))
        for code in cls.static_column_code.keys():
            setattr(total, f'm_{code}', getattr(total, f'm_{code}') - report.get(f'm_{code}', 0))
        report.save()
        total.save()

    @classmethod
    def add_done_item(cls, case_name, request):
        # print(f"{case_name}")
        site_id = request.POST.get("siteinfo_id")
        type_val = request.POST.get(f"{case_name}.done_type")
        isdone = (
            request.POST.get("isdone") is not None
            and request.POST.get("isdone") == "on"
        )
        site = SiteInfo.objects.get(id=site_id)
        y, m = get_year_month()
        done_report_obj = cls.objects.select_related("siteinfo").filter(
            siteinfo=site,
            done_type=type_val,
        )

        if done_report_obj.exists():
            done_report = done_report_obj.first()
        else:
            done_report = cls.objects.create(
                siteinfo=site,
                done_type=type_val,
                year=y,
                month=m,
                is_done=isdone,
                remark=request.POST.get(f"{case_name}.remark"),
            )

        for k, _ in done_report.static_column_code.items():
            value = Decimal(request.POST.get(f"{case_name}.m_{k}"))

            setattr(done_report, f"m_{k}", value)

        done_report.save()


class SteelItem(MonthReport):
    steel = models.ForeignKey(
        SteelReport,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        verbose_name="地點",
    )

    year = models.IntegerField(default=2010, verbose_name="年")
    month = models.IntegerField(default=1, verbose_name="月份")

    material = models.ForeignKey(
        Materials, on_delete=models.CASCADE, verbose_name="物料"
    )

    all_quantity = models.IntegerField(default=0, verbose_name="總數量")

    class Meta:
        unique_together = ["steel", "material", "all_quantity"]
        ordering = ["id"]  # 按照 id 升序排序
