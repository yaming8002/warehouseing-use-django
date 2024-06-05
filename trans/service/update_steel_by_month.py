from datetime import datetime
from decimal import Decimal
from stock.models.site_model import SiteInfo
from stock.models.steel_model import SteelReport
from trans.models.trans_model import TransLogDetail
from django.db.models import F
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from collections import defaultdict

from trans.service.update_board_by_month import conditional_sum


def update_steel_by_month(build_date):
    year, month = build_date.year, build_date.month
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = (
        first_day_of_month + relativedelta(months=1) - relativedelta(seconds=1)
    )
    update_steel_whse_by_month(first_day_of_month, last_day_of_month)

    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(material__mat_code__in=SteelReport.static_column_code.keys())
        & Q(translog__constn_site__genre__lte=1)
        & Q(is_rollback=False)
    )

    update_list = (
        TransLogDetail.objects.select_related("translog__constn_site", "material")
        .filter(query)
        .values(
            "translog__constn_site__code",  # sitecode
            "material__mat_code",  # mat_code
        )
        .annotate(
            quantity=conditional_sum("quantity"),
            all_unit_sum=conditional_sum("all_unit"),
        )
    )

    for x in update_list:
        siteinfo = SiteInfo.get_site_by_code(x["translog__constn_site__code"])
        column = f"m_{x['material__mat_code']}"
        value = (
            x["quantity"]
            if x["material__mat_code"] in ["92", "12", "13"]
            else x["all_unit_sum"]
        )
        SteelReport.update_column_value_by_before(
            siteinfo, year, month, False, column, value
        )


def update_steel_whse_by_month(first_day_of_month, last_day_of_month):
    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(material__mat_code__in=SteelReport.static_column_code.keys())
        & Q(is_rollback=False)
    )
    update_list = (
        TransLogDetail.objects.select_related("material")
        .filter(query)
        .values(
            mat_code=F("material__mat_code"),  # mat_code
        )
        .annotate(
            quantity=conditional_sum("quantity"),
            all_unit_sum=conditional_sum("all_unit"),
        )
    )

    site_whse = SiteInfo.get_site_by_code("0001")
    for x in update_list:
        column = f"m_{x['mat_code']}"
        value = (
            x["quantity"]
            if x["mat_code"] in ["92", "12", "13"]
            else x["all_unit_sum"]
        )
        SteelReport.update_column_value_by_before(
            site_whse,
            first_day_of_month.year,
            first_day_of_month.month,
            True,
            column,
            value,
        )
