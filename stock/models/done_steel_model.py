from datetime import datetime
from decimal import Decimal
from typing import Optional
from django.db import models
from stock.models.material_model import Materials
from stock.models.site_model import SiteInfo
from stock.models.steel_model import BaseSteelReport, SteelReport
from wcom.utils.uitls import get_year_month
import logging

# # Create your models here.
import logging.config
from django.conf import settings

logging.config.dictConfig(settings.LOGGING)

logger = logging.getLogger(__name__)


change_mapping = {
    '301':'300','351':'350','401':'400','4141':'414'
}

class DoneSteelReport(BaseSteelReport):

    trans_code = models.CharField( max_length=100, null=True, verbose_name="進出單號")

    turn_site = models.ForeignKey(
        SiteInfo,
        null=True,
        related_name="steel_trun_site",
        on_delete=models.CASCADE,
        verbose_name="轉單",
    )


    class Meta:
        unique_together = [
            (
                "siteinfo",
                "turn_site",
                "year",
                "month",
                "done_type",
                "is_done",
            )
        ]
        verbose_name = "變動資訊"
        verbose_name_plural = "變動資訊"
        ordering = ["done_type", "id"]  # 按照 id 升序排序

    @classmethod
    def whse_reomve_matials(
        cls,
        trans_code,
        mat: Materials,
        year: int,
        month: int,
        all_quantity: Decimal,
        all_unit: Decimal,
        remark: str,
    ):
        if cls.objects.filter(trans_code = trans_code).exists():
            return 
        if not year:
            now = datetime.now()
            year, month = now.year, now.month

        whse = SteelReport.get_current_by_site(
            SiteInfo.get_site_by_code("0001"), year, month
        )
        total = SteelReport.get_current_by_site(
            SiteInfo.get_site_by_code("0000"), year, month
        )

        column = f"m_{mat.mat_code}"
        value = all_quantity if mat.mat_code in ["92", "12", "13"] else all_unit
        setattr(whse, column, getattr(whse, column) - value)
        setattr(total, column, getattr(total, column) - value)
        cls.add_new_mat(
            trans_code,
            SiteInfo.get_site_by_code("0000"),
            None,
            year,
            month,
            mat.mat_code,
            all_quantity,
            all_unit,
            remark
        )

    @classmethod
    def add_new_mat(
        cls,
        trans_code,
        site: SiteInfo,
        turn_site:Optional[SiteInfo],
        year: int,
        month: int,
        mat_code: str,
        all_quantity: Decimal,
        all_unit: Decimal,
        remark: str,
    ):
        if cls.objects.filter(trans_code = trans_code).exists():
            return 
        column = f"m_{mat_code}"
        total = SteelReport.get_current_by_site(
            site=SiteInfo.get_site_by_code("0000"), year=year, month=month
        )
        donesteel, _ = cls.objects.get_or_create(
            siteinfo=site,
            turn_site=turn_site,
            year=year,
            month=month,
            done_type=2,
            is_done=True,
        )
        if mat_code in ["92", "12", "13"]:
            setattr(total, column, Decimal(getattr(total, column)) + all_quantity)
            setattr(
                donesteel, column, Decimal(getattr(donesteel, column)) + all_quantity
            )
        else:
            setattr(total, column, Decimal(getattr(total, column)) + all_unit)
            setattr(donesteel, column, Decimal(getattr(donesteel, column)) + all_unit)
        donesteel.remark = (
            f"{site.owner} {(remark if remark and remark !='None' else '')}"
        )
        total.save()
        donesteel.save()

    @classmethod
    def pile_to_board(
        cls,
        trans_code,
        site: SiteInfo,
        year: int,
        month: int,
        mat_code: str,
        all_unit: Decimal,
        remark: str,
    ):
        if cls.objects.filter(trans_code = trans_code).exists():
            return 
        column = f"m_{mat_code}"
        column_by = f"m_{change_mapping[mat_code]}"
        total = SteelReport.get_current_by_site(
            site=SiteInfo.get_site_by_code("0000"), year=year, month=month
        )
        donesteel, _ = cls.objects.get_or_create(
            siteinfo=site,
            year=year,
            month=month,
            done_type=2,
            is_done=True,
        )

        setattr(total, column, Decimal(getattr(total, column)) + all_unit)
        setattr(donesteel, column, Decimal(getattr(donesteel, column)) + all_unit)
        setattr(total, column_by, Decimal(getattr(total, column_by)) - all_unit)
        setattr(donesteel, column_by, Decimal(getattr(donesteel, column_by)) - all_unit)
        donesteel.remark = remark
        total.save()
        donesteel.save()


    @classmethod
    def roll_back(cls, site: SiteInfo):
        cls.objects.filter(siteinfo=site).update(**{"is_done": False})
        report = SteelReport.get_current_by_site(site)
        report.is_done = True
        total = SteelReport.get_current_by_site(SiteInfo.get_site_by_code("0000"))
        for code in cls.static_column_code.keys():
            setattr(
                total,
                f"m_{code}",
                getattr(total, f"m_{code}") - report.get(f"m_{code}", 0),
            )
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
