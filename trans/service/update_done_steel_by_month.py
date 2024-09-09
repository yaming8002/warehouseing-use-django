from datetime import datetime
from decimal import Decimal


from stock.models.done_steel_model import DoneSteelReport
from stock.models.material_model import Materials
from stock.models.site_model import SiteInfo
from stock.models.steel_model import SteelReport
from stock.models.stock_model import Stock
from trans.models.trans_model import TransLogDetail
from django.db.models import Q, F, Sum  # Ensure Sum is also imported
from collections import defaultdict

from trans.service.update_board_by_month import conditional_sum
from trans.utils import get_global_done_steel_list, get_global_steel_list

filtered_mat_codes = get_global_steel_list()

def reomve_total_steel(first_day_of_month,last_day_of_month):
    """倉庫物料轉廢料"""
    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(translog__transaction_type="OUT")
        & Q(translog__constn_site__code="0000")
        & Q(material__mat_code__in=filtered_mat_codes.values())
        & Q(is_rollback=False)
    )

    update_list = (
        TransLogDetail.objects.select_related("translog", "material")
        .filter(query)
        .values(
            mat_code=F("material__mat_code"),  # mat_code
        )
        .annotate(
            quantity=Sum("quantity"),
            all_unit_sum=Sum("all_unit"),
        )
    )
    # print(update_list.query)

    for detial in update_list:
        DoneSteelReport.whse_reomve_matials(
            detial["mat_code"],
            first_day_of_month.year,
            first_day_of_month.month,
            detial["quantity"],
            detial["all_unit_sum"],
        )


def update_done_steel_by_month(year, month,first_day_of_month,last_day_of_month):
    # 直接添加

    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(material__mat_code__in=filtered_mat_codes.keys())
        & Q(translog__transaction_type='IN')
        & ~Q(translog__constn_site__code__in=['F001','F002','F003'])
        & Q(remark__contains="#")
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
    print(update_list.query)
    for detial in update_list:
        site = SiteInfo.get_site_by_code(detial["site_code"])
        trun_site = SiteInfo.get_site_by_code(detial["trans_code"])
        column = f"m_{filtered_mat_codes[detial['mat_code']]}"
        value = (
            detial["quantity"]
            if filtered_mat_codes[detial['mat_code']] in ["102", "18", "19"]
            else detial["all_unit_sum"]
        )
        if trun_site:
            report = SteelReport.get_current_by_site(
                trun_site, first_day_of_month.year, first_day_of_month.month
            )
            setattr(report, column,getattr(report, column) +value)


        donesteel, _ = DoneSteelReport.objects.get_or_create(
            siteinfo=site,
            turn_site=trun_site,
            year=year,
            month=month,
            done_type=2,
            is_done=True,
            remark="採購"
        )
        setattr(donesteel, column, value)
        donesteel.save()


change_mapping = {"301": "300", "351": "350", "401": "400", "4141": "414"}

done_mat_codes = get_global_done_steel_list(True)

def update_done_steel_by_month_only_F(year, month,first_day_of_month,last_day_of_month):
    # 針對皓民的代號處理
    query = (
        Q(translog__build_date__range=(first_day_of_month, last_day_of_month))
        & Q(material__mat_code__in=done_mat_codes.keys())
        & Q(translog__constn_site__code__in=['F001','F002','F003'])
        & Q(is_rollback=False)
    )

    update_list = (
        TransLogDetail.objects.select_related("translog", "material")
        .filter(query)
        .values(
            mat_code=F("material__mat_code"),
            constn_code=F("translog__constn_site__code"),
            turn_code=F("translog__turn_site__code"),
            log_remark=F("remark")
        )
        .annotate(
            quantity=conditional_sum("quantity"),
            all_unit_sum=conditional_sum("all_unit"),
        )
    )
    f002_dct = defaultdict(lambda: Decimal(0))
    print(update_list.query)
    for detial in update_list:
        trun_site = (
            SiteInfo.get_site_by_code(detial["turn_code"])
            if detial["turn_code"]
            else None
        )
        trun_id = done_mat_codes[detial["mat_code"]]
        if "#" in detial["log_remark"] :
            if trun_id in ["16", "230"] and detial["quantity"] > 0 :
                """短接"""
                if '300' in detial['log_remark'] and trun_id =='16'  :
                    column ='m_358'
                elif '350' in detial['log_remark'] and trun_id =='16'  :
                    column ='m_295'
                elif '400' in detial['log_remark'] and trun_id =='16'  :
                    column ='m_424'
                elif '408' in detial['log_remark'] and trun_id =='16'  :
                    column ='m_170'
                elif trun_id =='230'  :
                    column ='m_193'

                donesteel, _ = DoneSteelReport.objects.get_or_create(
                    siteinfo=SiteInfo.get_site_by_code("F003"),
                    turn_site=trun_site,
                    year=year,
                    month=month,
                    done_type=2,
                    mat_code=detial["mat_code"],
                    is_done=True,
                    remark="轉短接 [米數需要調整]",
                )
                # setattr(steel_f, column, Decimal(getattr(steel_f, column)) - all_unit)
                DoneSteelReport.update_column_value(donesteel.id,False,column,detial["quantity"])
            elif trun_id in ['30', '31'] and detial["quantity"] > 0 :
                """斜撐"""
                column = f"m_{'358' if trun_id == '30' else '295' }"
                all_unit = detial["quantity"] * (
                    Decimal("1.25") if trun_id == "30" else Decimal(1.2)
                )
                f002_dct[column] -= all_unit
                donesteel, _ = DoneSteelReport.objects.get_or_create(
                    siteinfo=SiteInfo.get_site_by_code("F003"),
                    turn_site=trun_site,
                    year=year,
                    month=month,
                    done_type=2,
                    mat_code=detial["mat_code"],
                    is_done=True,
                    remark="轉斜撐",
                )
                DoneSteelReport.update_column_value(donesteel.id,False,column,all_unit)
            elif detial["quantity"] > 0 and detial["mat_code"] in filtered_mat_codes.keys() :
                value = (
                    detial["quantity"]
                    if trun_id in ["102", "18", "19"]
                    else detial["all_unit_sum"]
                )
                donesteel, _ = DoneSteelReport.objects.get_or_create(
                    siteinfo=SiteInfo.get_site_by_code("F001"),
                    turn_site=trun_site,
                    year=year,
                    month=month,
                    done_type=2,
                    is_done=True,
                    remark="採購",
                )
                DoneSteelReport.update_column_value(donesteel.id,True,f"m_{trun_id}",value)
            # setattr(donesteel, f"m_{detial['mat_code']}", value)
        elif detial["mat_code"] in change_mapping.keys() and detial["all_unit_sum"] > 0:
            """轉中柱"""
            donesteel, _ = DoneSteelReport.objects.get_or_create(
                siteinfo=SiteInfo.get_site_by_code(detial["constn_code"]),
                turn_site=trun_site,
                year=year,
                month=month,
                done_type=2,
                is_done=True,
                mat_code=detial["mat_code"],
                defaults={"remark": "轉中柱"},
            )
            column = f"m_{trun_id}"
            column_by = f"m_{done_mat_codes[change_mapping[detial['mat_code']]]}"
            f002_dct[column_by] -= detial["all_unit_sum"]
            setattr(
                donesteel,
                column,
                Decimal(detial["all_unit_sum"]),
            )
            setattr(
                donesteel,
                column_by,
                -Decimal(detial["all_unit_sum"]),
            )
            donesteel.mat_code = detial["mat_code"]
            donesteel.save()
        else:
            """正常的進出"""
            column = f"m_{trun_id}"
            value = (
                detial["quantity"]
                if trun_id in ["102", "18", "19"]
                else detial["all_unit_sum"]
            )
            f002_dct[column] -=value

    stock_f002 = SiteInfo.get_site_by_code("F002")
    # print(f002_dct)
    for k, v in f002_dct.items():
        SteelReport.update_column_value_by_before(stock_f002, year, month, True, k, v)

    site_f002 = SiteInfo.get_site_by_code("F002")
    wh = SteelReport.get_current_by_site(
        site_f002, first_day_of_month.year, first_day_of_month.month
    )

    for x in SteelReport.static_column_code.keys():
        value = getattr(wh, f"m_{x}")
        if x in ["102", "18", "19"]:
            x_queryset = Materials.objects.filter(mat_code=x)
            Stock.objects.filter(siteinfo=site_f002, material__in=x_queryset).update(
                quantity=value
            )
        else:
            x_queryset = Materials.objects.filter(mat_code=x, specification_id=23)
            Stock.objects.filter(siteinfo=site_f002, material__in=x_queryset).update(
                total_unit=value
            )



def update_total_by_month(year, month):
    """統整計算當月的總計"""

    update_list = (
        DoneSteelReport.objects.filter(year=year, month=month, is_done=True)
        .values("month")
        .annotate(
            total_358=Sum("m_358"),
            total_352=Sum("m_352"),
            total_295=Sum("m_295"),
            total_400=Sum("m_400"),
            total_424=Sum("m_424"),
            total_367=Sum("m_367"),
            total_170=Sum("m_170"),
            total_193=Sum("m_193"),
            total_265=Sum("m_265"),
            total_102=Sum("m_102"),
            total_18=Sum("m_18"),
            total_19=Sum("m_19"),
        )
    )

    if not update_list:
        return

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
