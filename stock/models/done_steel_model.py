from datetime import datetime
from decimal import Decimal
from typing import Optional
from django.db import models

from stock.models.site_model import SiteInfo
from stock.models.steel_model import BaseSteelReport, SteelReport
from wcom.utils.uitls import get_year_month
import logging

# # Create your models here.
import logging.config
from django.conf import settings

logging.config.dictConfig(settings.LOGGING)

logger = logging.getLogger(__name__)


class DoneSteelReport(BaseSteelReport):
    mat_code = models.CharField(
        max_length=20, default=None, null=True, verbose_name="物料編號"
    )
    """主要是針對皓民的物料資料進行分割"""
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
                "mat_code",
            )
        ]
        verbose_name = "變動資訊"
        verbose_name_plural = "變動資訊"
        ordering = ["done_type", "siteinfo", "id"]  # 按照 id 升序排序

    @classmethod
    def whse_reomve_matials(
        cls,
        mat_code: str,
        year: int,
        month: int,
        all_quantity: Decimal,
        all_unit: Decimal,
    ):
        if not year:
            now = datetime.now()
            year, month = now.year, now.month

        column = f"m_{mat_code}"
        value = all_quantity if mat_code in ["92", "12", "13"] else all_unit
        donesteel, _ = cls.objects.get_or_create(
            siteinfo=SiteInfo.get_site_by_code("0000"),
            year=year,
            month=month,
            done_type=2,
            is_done=True,
            remark="林口倉報廢",
        )
        setattr(donesteel, column, 0 - value)
        donesteel.save()

    @classmethod
    def add_new_mat(
        cls,
        site: SiteInfo,
        turn_site: Optional[SiteInfo],
        year: int,
        month: int,
        mat_code: str,
        all_quantity: Decimal,
        all_unit: Decimal,
        remark: Optional[str],
    ):
        column = f"m_{mat_code}"
        donesteel, _ = cls.objects.get_or_create(
            siteinfo=site,
            turn_site=turn_site,
            year=year,
            month=month,
            done_type=2,
            is_done=True,
            defaults={"remark": remark if remark else ""},
        )

        value = all_quantity if mat_code in ["92", "12", "13"] else all_unit
        setattr(donesteel, column, value)

        donesteel.save()
        return donesteel

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
        site_id = request.POST.get("siteinfo_id")
        y, m = get_year_month(request.POST.get("yearMonth"))
        type_val = request.POST.get(f"{case_name}.done_type")
        isdone = (
            request.POST.get("isdone") is not None
            and request.POST.get("isdone") == "on"
        )
        site = SiteInfo.objects.get(id=site_id)

        done_report_obj = (
            cls.objects.select_related("siteinfo")
            .filter(
                siteinfo=site,
                year=y,
                month=m,
                done_type=type_val,
            )
            .order_by("-year", "-month")
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
            value = request.POST.get(f"{case_name}.m_{k}")
            value = Decimal(value) if value else Decimal(0)
            setattr(done_report, f"m_{k}", value)

        done_report.save()
