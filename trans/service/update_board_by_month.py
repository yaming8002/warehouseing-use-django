from datetime import datetime
from decimal import Decimal
from stock.models.board_model import BoardReport
from stock.models.site_model import SiteInfo
from trans.models import TransLogDetail
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.db.models import Case, When, Value, Sum, DecimalField, F

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

def update_board_by_month(build_date):
    year, month = build_date.year, build_date.month
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = (
        first_day_of_month + relativedelta(months=1) - relativedelta(seconds=1)
    )

    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & (
            Q(material__mat_code__in=["22", "2205", "95"])
            | (Q(material__mat_code="92") & Q(remark__iregex=r"(?i)簍空|鏤空"))
        )
        & Q(is_rent=False)
        & Q(is_rollback=False)
    )

    update_list = (
        TransLogDetail.objects.select_related(
            "translog", "translog__constn_site", "material"
        )
        .filter(query)
        .values(
           site_code=F( "translog__constn_site__code"), 
           genre=F("translog__constn_site__genre"),
           mat_code=F("material__mat_code")
        )
        .annotate(
            sum_quantity=conditional_sum("quantity"),
        )
    )

    print(update_list.query)
    whse_dct = {}
    for x in update_list:
        siteinfo = SiteInfo.get_site_by_code(x["site_code"])
        column = x["mat_code"]
        if x["genre"] == 1 or x["site_code"]=='0003' :
            BoardReport.update_column_value_by_before(
                siteinfo, year, month, False, column, x["sum_quantity"]
            )
        if column not in whse_dct.keys():
            whse_dct[column] = Decimal(0)
        whse_dct[column] += x["sum_quantity"]
        
    site_whse = SiteInfo.get_site_by_code("0001")
    for k, v in whse_dct.items():
        BoardReport.update_column_value_by_before(site_whse, year, month, True, k, v)
