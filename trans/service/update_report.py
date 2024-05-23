from datetime import datetime
from decimal import Decimal
from stock.models.board_model import BoardReport
from stock.models.done_steel_model import DoneSteelReport, change_mapping
from stock.models.rail_model import RailReport
from stock.models.site_model import SiteInfo
from stock.models.steel_model import SteelReport
from trans.models.trans_model import TransLogDetail
from django.db.models import Case, When, Value, Sum, DecimalField, F
from dateutil.relativedelta import relativedelta
from django.db.models import F, Q, Window
from collections import defaultdict

from wcom.utils.uitls import is_whse_code


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
    last_day_of_month = (
        first_day_of_month + relativedelta(months=1) - relativedelta(seconds=1)
    )
    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & (
            Q(material__mat_code="3050")
            | (Q(material__mat_code="999") & Q(remark__icontains="鋼軌"))
        )
        & Q(is_rent=False)
        & Q(is_rollback=False)
    )
    update_list = (
        TransLogDetail.objects.select_related(
            "translog", "translog__siteinfo", "material"
        )
        .filter(query)
        .values(
            site_code=F("translog__constn_site__code"),  # sitecode
            site_genre=F("translog__constn_site__genre"),  # sitecode genre
            mat_code=F("material__mat_code"),  # mat_code
            trans_type=F("translog__transaction_type"),  # transaction_type
            spec_id=F("material__specification_id"),  # specification_id
        )
        .annotate(quantity=Sum("quantity"), unit_sum=Sum("unit"))
    )

    whse_dct = defaultdict(lambda: Decimal(0))
    total_dct = defaultdict(lambda: Decimal(0))
    for x in update_list:
        is_in = x["trans_type"] == "IN"
        siteinfo = SiteInfo.get_site_by_code(x["site_code"])
        spec_id = x["spec_id"]
        column = f"in_{spec_id}" if is_in else f"out_{spec_id}"
        column = "rail_ng" if '25' in column else column
        if x["site_genre"] == 1:
            RailReport.update_column_value_by_before(
                siteinfo, year, month, True, column, x["quantity"]
            )
            RailReport.count_total(siteinfo, year, month, is_in)
        if column == "rail_ng":
            continue
        if x["site_genre"] > 1:
            total_dct[spec_id] += x["quantity"] if is_in else -x["quantity"]
            total_dct["total"] += x["quantity"] if is_in else -x["quantity"]
        whse_dct[spec_id] += x["quantity"] if is_in else -x["quantity"]
        whse_dct["total"] += x["quantity"] if is_in else -x["quantity"]

    site_whse = SiteInfo.get_site_by_code("0001")
    site_total = SiteInfo.get_site_by_code("0000")
    # print(whse_dct)
    for k, v in whse_dct.items():
        RailReport.update_column_value_by_before(
            site_whse, year, month, True, f"in_{k}", v
        )
    site_total = SiteInfo.get_site_by_code("0000")
    for k, v in total_dct.items():
        RailReport.update_column_value_by_before(
            site_total, year, month, True, f"in_{k}", v
        )


def update_steel_by_month(build_date):
    year, month = build_date.year, build_date.month
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = (
        first_day_of_month + relativedelta(months=1) - relativedelta(seconds=1)
    )
    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(material__mat_code__in=SteelReport.static_column_code.keys())
        & Q(translog__constn_site__genre=1)
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
            unit_sum=conditional_sum("unit"),
            all_unit_sum=conditional_sum("all_unit"),
        )
    )

    whse_dct = defaultdict(lambda: Decimal(0))

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
        whse_dct[column] += value
        # if check_new_mat():

    site_whse = SiteInfo.get_site_by_code("0001")
    for k, v in whse_dct.items():
        SteelReport.update_column_value_by_before(site_whse, year, month, True, k, v)


def update_done_steel_by_month(build_date):
    year, month = build_date.year, build_date.month
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = (
        first_day_of_month + relativedelta(months=1) - relativedelta(seconds=1)
    )

    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & (
            Q(translog__transaction_type="IN")
            | (
                Q(translog__transaction_type="OUT")
                & Q(translog__constn_site__code="0000")
            )
        )
        & Q(material__mat_code__in=SteelReport.static_column_code.keys())
        & ~Q(translog__constn_site__genre=1)
        & Q(is_rollback=False)
    )

    update_list = (
        TransLogDetail.objects.select_related("translog", "material")
        .filter(query)
        .all()
    )

    whse_dct = defaultdict(lambda: Decimal(0))

    for detial in update_list:
        if (
            detial.translog.constn_site.code == "0000"
            and detial.translog.transaction_type == "OUT"
        ):
            DoneSteelReport.whse_reomve_matials(
                detial.translog.code,
                detial.material,
                year,
                month,
                detial.quantity,
                detial.all_unit,
                detial.remark,
            )
        elif detial.translog.constn_site.code == "F002":
            if detial.material.mat_code in ["301", "351", "401", "4141"]:
                DoneSteelReport.pile_to_board(
                    detial.translog.code,
                    detial.translog.constn_site,
                    year,
                    month,
                    detial.material.mat_code,
                    detial.all_unit,
                    "支撐轉中柱",
                )

        elif detial.translog.constn_site.code in ["G001", "F003"] and not is_whse_code(
            detial.translog.code
        ):
            siteinfo = SiteInfo.get_site_by_code(detial.translog.constn_site.code)
            column = f"m_{detial.material.mat_code}"
            value = detial.quantity
            SteelReport.update_column_value_by_before(
                siteinfo, year, month, False, column, value
            )
            whse_dct[column] += value
        else:
            DoneSteelReport.add_new_mat(
                detial.translog.code,
                detial.translog.constn_site,
                detial.translog.turn_site,
                year,
                month,
                detial.material.mat_code,
                detial.quantity,
                detial.all_unit,
                detial.remark,
            )

    site_whse = SiteInfo.get_site_by_code("0001")
    for k, v in whse_dct.items():
        SteelReport.update_column_value_by_before(site_whse, year, month, True, k, v)


def update_board_by_month(build_date):
    year, month = build_date.year, build_date.month
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = (
        first_day_of_month + relativedelta(months=1) - relativedelta(seconds=1)
    )
    mat_codes = ['22','2205','95']
    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & (
            Q(material__mat_code__in=mat_codes)
            | (Q(material__mat_code="92") & Q(remark__icontains="簍空"))
        )
        & Q(is_rent=False)
        & Q(is_rollback=False)
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
    site_whse = SiteInfo.get_site_by_code("0001")
    whse_dct = {}
    for x in update_list:
        siteinfo = SiteInfo.get_site_by_code(x["translog__constn_site__code"])
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
