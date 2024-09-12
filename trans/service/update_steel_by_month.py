from stock.models.material_model import Materials
from stock.models.site_model import SiteInfo
from stock.models.steel_model import SteelReport
from stock.models.stock_model import Stock
from trans.models.trans_model import TransLogDetail
from django.db.models import F
from django.db.models import Q


from trans.service.update_board_by_month import conditional_sum
from trans.utils import get_global_steel_list

filtered_mat_codes = get_global_steel_list()


def update_steel_by_month(year, month, first_day_of_month, last_day_of_month):
    query_by_month = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(
            material__mat_code__in=filtered_mat_codes.keys()
        )
        & (
            Q(translog__constn_site__genre__gte=1)
            | Q(translog__constn_site__code="0003")
        )
        & ~Q(translog__constn_site__code__in=['F001','F002','F003'])
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
            x["quantity"] if filtered_mat_codes[x['mat_code']] in ["102", "18", "19"] else x["all_unit_sum"]
        )
        if siteinfo.genre != 6:
            SteelReport.update_column_value_by_before(
                siteinfo, year, month, False, column, value
            )

    update_steel_whse_by_month(first_day_of_month, last_day_of_month)


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
    site_whse = SiteInfo.get_site_by_code("0001")
    for x in update_list:
        column = f"m_{filtered_mat_codes[x['mat_code']]}"
        value = (
            x["quantity"] if filtered_mat_codes[x['mat_code']] in ["102", "18", "19"] else x["all_unit_sum"]
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
