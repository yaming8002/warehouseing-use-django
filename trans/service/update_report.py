from datetime import datetime
from decimal import Decimal
from stock.models.board_model import BoardReport
from stock.models.rail_model import RailReport
from stock.models.site_model import SiteInfo
from stock.models.steel_model import SteelReport
from trans.models.trans_model import TransLogDetail
from django.db.models import Case, When, Value, Sum, DecimalField, F
from dateutil.relativedelta import relativedelta
from django.db.models import F, Q, Window
from collections import defaultdict


def conditional_sum(field_name):
    """Returns a conditional sum expression for a given field using DecimalField."""
    return Sum(
        Case(
            When(translog__transaction_type="IN", then=F(field_name)),
            When(translog__transaction_type="OUT", then=-F(field_name)),
            default=Value(0),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )
    )


def update_rail_by_month(build_date):
    year, month = build_date.year, build_date.month
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = first_day_of_month + relativedelta(months=1)
    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(material__mat_code="3050")
        & (
            (~Q(material__mat_code="999"))
            | (Q(material__mat_code="999") & Q(remark__icontains="鋼軌"))
        )
        & Q(is_rent=False)
    )
    update_list = (
        TransLogDetail.objects.select_related(
            "translog", "translog__siteinfo", "material"
        )
        .filter(query)
        .values(
            "translog__constn_site__code",  # sitecode
            "translog__constn_site__genre",  # sitecode genre
            "material__mat_code",  # mat_code
            "translog__transaction_type",  # transaction_type
            "material__specification_id",  # specification_id
        )
        .annotate(quantity=Sum("quantity"), unit_sum=Sum("unit"))
    )

    whse_dct = defaultdict(lambda: Decimal(0))
    total_dct = defaultdict(lambda: Decimal(0))
    for x in update_list:
        is_in = x["translog__transaction_type"] == "IN"
        siteinfo = SiteInfo.objects.get(code=x["translog__constn_site__code"])
        spec_id = x["material__specification_id"]
        column = f"in_{spec_id}" if is_in else f"out_{spec_id}"
        total_col = "in_total" if is_in else "out_total"
        if x["translog__constn_site__genre"] == 1:
            RailReport.update_column_value_by_before(
                siteinfo, year, month, True, column, x["quantity"]
            )
            RailReport.count_total(siteinfo, year, month, is_in)
        if x["translog__constn_site__genre"] > 1:
            total_dct[spec_id] += x["quantity"] if is_in else -x["quantity"]
            total_dct["total"] += x["quantity"] if is_in else -x["quantity"]
        whse_dct[spec_id] += x["quantity"] if is_in else -x["quantity"]
        whse_dct["total"] += x["quantity"] if is_in else -x["quantity"]

    print(whse_dct)
    site_whse = SiteInfo.objects.get(code="0001")
    site_total = SiteInfo.objects.get(code="0000")
    for k, v in whse_dct.items():
        RailReport.update_column_value_by_before(
            site_whse, year, month, True, f"in_{k}", v
        )
    for k, v in total_dct.items():
        RailReport.update_column_value_by_before(
            site_total, year, month, True, f"in_{k}", v
        )


def update_steel_by_month(build_date):
    year, month = build_date.year, build_date.month
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = first_day_of_month + relativedelta(months=1)
    query = Q(translog__build_date__range=(first_day_of_month, last_day_of_month)) & Q(
        material__mat_code__in=SteelReport.static_column_code.keys()
    ) & Q(translog__constn_site__genre =1)
    update_list = (
        TransLogDetail.objects.select_related("translog__siteinfo", "material")
        .filter(query)
        .values(
            "translog__constn_site__code",  # sitecode
            "material__mat_code",  # mat_code
        )
        .annotate(
            quantity=conditional_sum("quantity"),
            unit_sum=conditional_sum("unit"),
            all_unit_sum=conditional_sum("all_unit"),
        )
    )

    whse_dct = defaultdict(lambda: Decimal(0))

    for x in update_list:
        siteinfo = SiteInfo.objects.get(code=x["translog__constn_site__code"])
        column = f"m_{x['material__mat_code']}"
        value = (
            x["quantity"]
            if x["material__mat_code"] in ["92", "12", "13"]
            else x["all_unit_sum"]
        )
        SteelReport.update_column_value_by_before(
            siteinfo, year, month, False, column, value
        )
        whse_dct[column] += value
        # if check_new_mat():

    site_whse = SiteInfo.objects.get(code="0001")
    for k, v in whse_dct.items():
        SteelReport.update_column_value_by_before(site_whse, year, month, True, k, v)


def check_new_mat(item: dict):
    if item["translog__constn_site__genre"] == 1:
        return False
    return True


def update_board_by_month(build_date):
    year, month = build_date.year, build_date.month
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = first_day_of_month + relativedelta(months=1)
    mat_codes = BoardReport.static_column_code.keys()
    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(material__mat_code__in=mat_codes)
        & (
            (~Q(material__mat_code="92"))
            | (Q(material__mat_code="92") & Q(remark__icontains="簍空"))
        )
        & Q(is_rent=False)
    )

    update_list = (
        TransLogDetail.objects.select_related(
            "translog", "translog__siteinfo", "material"
        )
        .filter(query)
        .values(
            "translog__constn_site__code",  # sitecode
            "translog__constn_site__genre",  # sitecode genre
            "material__mat_code",  # mat_code
        )
        .annotate(
            quantity=conditional_sum("quantity"),
        )
    )
    print(update_list.query)
    site_whse = SiteInfo.objects.get(code="0001")
    whse_dct = {}
    for x in update_list:
        siteinfo = SiteInfo.objects.get(code=x["translog__constn_site__code"])
        column = x["material__mat_code"]
        if x["translog__constn_site__genre"] == 1:
            BoardReport.update_column_value_by_before(
                siteinfo, year, month, False, column, x["quantity"]
            )
        if column not in whse_dct.keys():
            whse_dct[column] = Decimal(0)
        whse_dct[column] += x["quantity"]
    for k, v in whse_dct.items():
        BoardReport.update_column_value_by_before(site_whse, year, month, True, k, v)
