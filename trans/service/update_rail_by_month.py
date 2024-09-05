from decimal import Decimal

from django.forms import model_to_dict

from stock.models.rail_model import RailReport
from stock.models.site_model import SiteInfo
from trans.models.trans_model import TransLogDetail
from django.db.models import Sum, F
from django.db.models import Q
from collections import defaultdict


def update_rail_by_month(year, month, first_day_of_month, last_day_of_month):
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

    # print('rail query',update_list.query)
    whse_dct = defaultdict(lambda: Decimal(0))
    for x in update_list:
        is_in = x["trans_type"] == "IN"
        siteinfo = SiteInfo.get_site_by_code(x["site_code"])
        spec_id = x["spec_id"]
        if not (spec_id < 23 or spec_id == 25):
            continue
        column = f"in_{spec_id}" if is_in else f"out_{spec_id}"
        column = "rail_ng" if "25" in column else column
        if x["site_genre"] == 1:
            RailReport.update_column_value_by_before(
                siteinfo, year, month, True, column, x["quantity"]
            )
            RailReport.count_total(siteinfo, year, month, is_in)
        if column == "rail_ng":
            continue
        whse_dct[spec_id] += x["quantity"] if is_in else -x["quantity"]
    site_whse = SiteInfo.get_warehouse()
    for k, v in whse_dct.items():
        RailReport.update_column_value_by_before(
            site_whse, year, month, True, f"in_{k}", v
        )
    RailReport.count_total(site_whse, year, month, True)
    count_done_report(year, month)


def count_done_report( year, month):
    total = SiteInfo.get_site_by_code("0000")
    total_dct = defaultdict(lambda: Decimal(0))
    query = Q(siteinfo__id__gt=1)  & (Q(year__lt=year) | Q(year=year, month__lte=month))
    final_query = Q()
    lst = RailReport.get_current_by_query(query, final_query)
    for rail in lst:
        for i in range(5, 17):
            if rail.siteinfo.id == 2:
                total_dct[i] += getattr(rail, f"in_{i}", 0)
            else:
                total_dct[i] += getattr(rail, f"out_{i}", 0) - getattr(
                    rail, f"in_{i}", 0
                )

    total_report = RailReport.get_current_by_site(total, year, month)
    for k, v in total_dct.items():
        setattr(total_report, f"in_{k}", v)
    total_report.save()
    RailReport.count_total(total, year, month, True)
