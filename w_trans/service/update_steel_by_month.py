from collections import defaultdict
from decimal import Decimal

from django.db.models import F, Q

from w_stock.models.material_model import Materials
from w_stock.models.site_model import SiteInfo

from w_stock.models.stock_model import Stock
from w_trans.models.trans_model import TransLogDetail
from w_trans.service.update_board_by_month import conditional_sum
from w_trans.utils import get_global_steel_list
from w_whreport.models.steel_model import SteelReport

filtered_mat_codes = get_global_steel_list()


def update_steel_by_month(year, month, first_day_of_month, last_day_of_month):
    query_by_month = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(material__mat_code__in=filtered_mat_codes.keys())
        & (
            Q(translog__constn_site__genre__gte=1)
            | Q(translog__constn_site__code="0003")
        )
        & ~Q(translog__constn_site__code__in=["F001", "F002", "F003"])
        & ~( Q(remark__contains="#") & Q(translog__transaction_type='IN'))
        & Q(is_rollback=False)
    )

    update_list = (
        TransLogDetail.objects.select_related("translog__constn_site", "material")
        .filter(query_by_month)
        .values(
            site_code=F("translog__constn_site__code"),  # sitecode
            genre=F("translog__constn_site__genre"),  # sitecode
            mat_code=F("material__mat_code"),  # mat_code
        )
        .annotate(
            quantity=conditional_sum("quantity"),
            all_unit_sum=conditional_sum("all_unit"),
        )
    )

    for x in update_list:
        siteinfo = SiteInfo.get_site_by_code(x["site_code"])

        column = f"m_{filtered_mat_codes[x['mat_code']]}"
        value = (
            x["quantity"]
            if filtered_mat_codes[x["mat_code"]] in ["102", "18", "19"]
            else x["all_unit_sum"]
        )
        # if siteinfo.genre != 6 :
        SteelReport.update_column_value_by_before(
            siteinfo, year, month, False, column, value
        )

    update_steel_whse_by_month(first_day_of_month, last_day_of_month)
    # update_steel_total_by_month(year,month)


def update_steel_whse_by_month(first_day_of_month, last_day_of_month):
    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(material__mat_code__in=filtered_mat_codes.keys())
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
    # print(update_list.query)
    site_whse = SiteInfo.get_site_by_code("0001")
    for x in update_list:
        column = f"m_{filtered_mat_codes[x['mat_code']]}"
        value = (
            x["quantity"]
            if filtered_mat_codes[x["mat_code"]] in ["102", "18", "19"]
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

    wh = SteelReport.get_current_by_site(
        site_whse, first_day_of_month.year, first_day_of_month.month
    )

    for x in SteelReport.static_column_code.keys():
        value = getattr(wh, f"m_{x}")
        # print(x , value )
        if x in ["102", "18", "19"]:
            x_queryset = Materials.objects.filter(mat_code=x)
            Stock.objects.filter(siteinfo=site_whse, material__in=x_queryset).update(
                quantity=value
            )
        else:
            x_queryset = Materials.objects.filter(mat_code=x, specification_id=23)
            Stock.objects.filter(siteinfo=site_whse, material__in=x_queryset).update(
                total_unit=value
            )


def update_steel_total_by_month(year, month):
    query = Q(siteinfo__id__gt=1) & (Q(year__lt=year) | Q(year=year, month__lte=month))
    exclude_query = Q()
    for x in SteelReport.static_column_code.keys():
        exclude_query |= ~Q(**{f"m_{x}": 0})
    total_month = SteelReport.get_current_by_query(query, final_query=exclude_query)
    total_dct = defaultdict(Decimal)  # 改用float以支援小數
    i = 0
    for item in total_month:
        for x in SteelReport.static_column_code.keys():
            total_dct[f"m_{x}"] += round(
                getattr(item, f"m_{x}", 0), 2
            )  # 加入預設值0，以防字段不存在
        i+=1

    total = SteelReport.get_current_by_site(
        SiteInfo.get_site_by_code("0000"), year, month
    )

    for k, v in total_dct.items():
        setattr(total, k, v)
    total.save()
