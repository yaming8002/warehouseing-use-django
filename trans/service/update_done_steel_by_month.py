from datetime import datetime
from decimal import Decimal


from stock.models.done_steel_model import DoneSteelReport
from stock.models.material_model import Materials
from stock.models.site_model import SiteInfo
from stock.models.steel_model import SteelReport
from trans.models.trans_model import TransLogDetail
from dateutil.relativedelta import relativedelta
from django.db.models import Q, F, Sum  # Ensure Sum is also imported
from collections import defaultdict

from trans.service.update_board_by_month import conditional_sum


def reomve_total_steel(first_day_of_month, last_day_of_month):
    """倉庫物料轉廢料"""
    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(translog__transaction_type="OUT")
        & ~Q(translog__constn_site__genre=1)
        & ~Q(translog__constn_site__code="0003")
        & ~Q(translog__constn_site__code__startswith="F")
        & Q(material__mat_code__in=SteelReport.static_column_code.keys())
        & Q(is_rollback=False)
    )

    update_list = (
        TransLogDetail.objects.select_related("translog", "material")
        .filter(query)
        .values(
            site_code=F("translog__constn_site__code"),
            mat_code=F("material__mat_code"),  # mat_code
        )
        .annotate(
            quantity=Sum("quantity"),
            all_unit_sum=Sum("all_unit"),
        )
    )
    # print(update_list.query)

    for detial in update_list:
        if detial["site_code"] == "0000":
            DoneSteelReport.whse_reomve_matials(
                detial["mat_code"],
                first_day_of_month.year,
                first_day_of_month.month,
                detial["quantity"],
                detial["all_unit_sum"],
            )
        else:
            # 到維護廠處裡
            column = f"m_{detial['mat_code']}"
            value = (
                detial["quantity"]
                if detial["mat_code"] in ["92", "12", "13"]
                else detial["all_unit_sum"]
            )
            SteelReport.update_column_value_by_before(
                SiteInfo.get_site_by_code(detial["site_code"]),
                first_day_of_month.year,
                first_day_of_month.month,
                True,
                column,
                value,
            )


def update_done_steel_by_month(build_date):
    year, month = build_date.year, build_date.month
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = (
        first_day_of_month + relativedelta(months=1) - relativedelta(seconds=1)
    )
    reomve_total_steel(first_day_of_month, last_day_of_month)
    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(translog__transaction_type="IN")
        & Q(translog__constn_site__genre__gt=1)
        & Q(material__mat_code__in=SteelReport.static_column_code.keys())
        & ~Q(translog__constn_site__code__startswith="F")
        & Q(is_rollback=False)
    )

    update_list = (
        TransLogDetail.objects.select_related("translog", "material")
        .filter(query)
        .values(
            site_code=F("translog__constn_site__code"),  # sitecode
            trans_code=F("translog__turn_site__code"),  # sitecode
            trans_type=F("translog__transaction_type"),  # transaction_type
            mat_code=F("material__mat_code"),  # mat_code
        )
        .annotate(
            quantity=Sum("quantity"),
            all_unit_sum=Sum("all_unit"),
        )
    )
    # print(update_list.query)

    for detial in update_list:
        site = SiteInfo.get_site_by_code(detial["site_code"])
        turn_site = (
            SiteInfo.get_site_by_code(detial["trans_code"])
            if detial["trans_code"]
            else None
        )
        DoneSteelReport.add_new_mat(
            site,
            turn_site,
            year,
            month,
            detial["mat_code"],
            detial["quantity"],
            detial["all_unit_sum"],
            "",
        )


change_mapping = {"301": "300", "351": "350", "401": "400", "4141": "414"}

mat_list = [
    "300","301","350","351","390","400","401","408","414",
    "4141","92","12","13","2301","2302","10","4144",
]


def update_done_steel_by_month_only_F(build_date):
    # 針對皓民的代號處理
    year, month = build_date.year, build_date.month
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = (
        first_day_of_month + relativedelta(months=1) - relativedelta(seconds=1)
    )

    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(material__mat_code__in=mat_list)
        & Q(translog__constn_site__code__startswith="F")
        & Q(is_rollback=False)
    )

    update_list = (
        TransLogDetail.objects.select_related(
            "translog", "translog__constn_site", "translog__turn_site", "material"
        )
        .filter(query)
        .all()
    )

    print(update_list.query)

    f002_dct = defaultdict(lambda: Decimal(0))
    for detial in update_list:
        if detial.translog.transaction_type == "OUT":
            column = f"m_{detial.material.mat_code}"
            if detial.material.mat_code not in SteelReport.static_column_code:
                continue
            value = (
                detial.quantity
                if detial.material.mat_code in ["92", "12", "13"]
                else detial.all_unit
            )
            f002_dct[column] += value
        elif DoneSteelReport.objects.filter(trans_code=detial.translog.code).exists():
            continue
        elif detial.material.mat_code in ["2301", "2302"]:
            """斜撐"""
            print("""斜撐""")
            column = f"m_{'300' if detial.material.mat_code=='2301' else '350' }"
            all_unit = detial.quantity * (
                Decimal('1.25') if detial.material.mat_code == "2301" else Decimal(1.2)
            )
            # setattr(steel_f,column,getattr(steel_f,column) - all_unit)
            f002_dct[column] -= all_unit
            DoneSteelReport.add_new_mat(
                SiteInfo.get_site_by_code("F002"),
                detial.translog.turn_site,
                year,
                month,
                "300" if detial.material.mat_code == "2301" else "350",
                detial.quantity,
                -all_unit,
                f"轉斜撐   {detial.remark}",
            )
        elif detial.material.mat_code in ["10", "4144"]:
            """短接"""
            print("""短接""")
            column = f"m_{'350' if detial.material.mat_code=='10' else detial.material.mat_code[:-1] }"
            donesteel, _ = DoneSteelReport.objects.get_or_create(
                siteinfo=detial.translog.constn_site,
                turn_site=detial.translog.turn_site,
                year=year,
                month=month,
                done_type=2,
                is_done=True
            )
            # setattr(steel_f, column, Decimal(getattr(steel_f, column)) - all_unit)
            donesteel.remark = f"轉短接 [米數需要調整]   {detial.remark}"
            setattr(
                donesteel, column, Decimal(getattr(donesteel, column)) + detial.quantity
            )
            donesteel.save()
        elif detial.material.mat_code in change_mapping.keys():
            print("""轉中柱""")
            """轉中柱"""
            donesteel, _ = DoneSteelReport.objects.get_or_create(
                siteinfo=detial.translog.constn_site,
                turn_site=detial.translog.turn_site,
                year=year,
                month=month,
                done_type=2,
                is_done=True,
                defaults={
                    "remark":f"轉中柱   {detial.remark}"
                }
            )
            column = f"m_{detial.material.mat_code}"
            column_by = f"m_{change_mapping[detial.material.mat_code]}"
            f002_dct[column_by] -= detial.all_unit
            print(Decimal(getattr(donesteel, column)) + Decimal(detial.all_unit))
            print(
                Decimal(getattr(donesteel, column_by)) - Decimal(detial.all_unit),
            )
            setattr(
                donesteel,
                column,
                Decimal(getattr(donesteel, column)) + Decimal(detial.all_unit),
            )
            setattr(
                donesteel,
                column_by,
                Decimal(getattr(donesteel, column_by)) - Decimal(detial.all_unit),
            )
            donesteel.save()
        elif detial.material.mat_code in change_mapping.values():
            siteinfo = SiteInfo.get_site_by_code("F002")
            column = f"m_{detial.material.mat_code}"
            value = (
                detial.quantity
                if detial.material.mat_code in ["92", "12", "13"]
                else detial.all_unit
            )
            SteelReport.update_column_value_by_before(
                siteinfo, year, month, False, column, value
            )
            f002_dct[column] -= value
        # if check_new_mat():

    stock_f002 = SiteInfo.get_site_by_code("F002")
    # print(f002_dct)
    for k, v in f002_dct.items():
        SteelReport.update_column_value_by_before(stock_f002, year, month, True, k, v)

    update_total_by_month(year, month)


def update_total_by_month(year, month):
    """統整計算當月的總計"""

    update_list = (
        DoneSteelReport.objects.filter(year=year, month=month, is_done=True)
        .values("month")
        .annotate(
            total_300=Sum("m_300"),
            total_301=Sum("m_301"),
            total_350=Sum("m_350"),
            total_351=Sum("m_351"),
            total_400=Sum("m_400"),
            total_401=Sum("m_401"),
            total_408=Sum("m_408"),
            total_414=Sum("m_414"),
            total_4141=Sum("m_4141"),
            total_92=Sum("m_92"),
            total_12=Sum("m_12"),
            total_13=Sum("m_13"),
        )
    )

    site_whse = SiteInfo.get_site_by_code("0000")
    for k, v in update_list[0].items():
        if k == "month":
            continue
        column = k.replace("total_", "m_")
        SteelReport.update_column_value_by_before(
            site_whse,
            year,
            month,
            True,
            column,
            v,
        )
