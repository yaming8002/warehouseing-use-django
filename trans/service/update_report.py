from datetime import datetime
import pdb
from stock.models.done_steel_model import DoneSteelReport
from stock.models.steel_model import SteelReport
from trans.models.trans_model import TransLog, TransLogDetail
from trans.service.update_board_by_month import update_board_by_month
from trans.service.update_done_steel_by_month import (
    reomve_total_steel,
    update_done_steel_by_month,
    update_done_steel_by_month_only_F,
    update_total_by_month,
)
from trans.service.update_rail_by_month import update_rail_by_month
from trans.service.update_steel_by_month import update_steel_by_month
from dateutil.relativedelta import relativedelta
from wcom.utils.excel_tool import execute_stored_procedure

sql_command = "CALL proc_stock_summary(%s, %s, %s)"

def count_all_report(count_date: datetime):
    year, month = count_date.year, count_date.month
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = (
        first_day_of_month + relativedelta(months=1) - relativedelta(seconds=1)
    )
    execute_stored_procedure(sql_command, [first_day_of_month, last_day_of_month, True])
    print("execute_stored_procedure is run ")
    update_rail_by_month(
        year, month, first_day_of_month, last_day_of_month
    )  # 鋼軌的計算
    update_board_by_month(
        year, month, first_day_of_month, last_day_of_month
    )  # 鐵板的計算
    update_steel_by_month(
        year, month, first_day_of_month, last_day_of_month
    )  # 一般工地的鋼樁計算
    reomve_total_steel(year, month, first_day_of_month, last_day_of_month)  # 材料類棄用
    update_done_steel_by_month(year, month, first_day_of_month, last_day_of_month)
    update_done_steel_by_month_only_F(
        year, month, first_day_of_month, last_day_of_month
    )  # 皓民
    update_total_by_month(year, month)  # 重新統計當月份總物料


def move_old_data_by_month(year, month):
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = (
        first_day_of_month + relativedelta(months=1) - relativedelta(seconds=1)
    )
    logs = TransLog.objects.filter(
        build_date__range=(first_day_of_month, last_day_of_month)
    )
    if logs.exists():
        execute_stored_procedure(sql_command, [first_day_of_month, last_day_of_month, False])
        details = TransLogDetail.objects.filter(translog__in=logs)
        if details.exists():
            details.delete()
        if logs.exists():
            logs.delete()
    report = SteelReport.objects.filter(year=year,month=month,done_type=0)
    if report.exists():
        report.delete()
    report = DoneSteelReport.objects.filter(year=year,month=month,done_type=2)
    if report.exists():
        report.delete()   
