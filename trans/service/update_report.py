

from datetime import datetime
from trans.service.update_board_by_month import update_board_by_month
from trans.service.update_done_steel_by_month import reomve_total_steel, update_done_steel_by_month,  update_done_steel_by_month_only_F, update_total_by_month
from trans.service.update_rail_by_month import update_rail_by_month
from trans.service.update_steel_by_month import update_steel_by_month


def count_all_report(count_date:datetime):
    update_rail_by_month(count_date) # 鋼軌的計算
    update_board_by_month(count_date) # 鐵板的計算
    update_steel_by_month(count_date) # 一般工地的鋼樁計算
    reomve_total_steel(count_date) # 材料類棄用
    update_done_steel_by_month(count_date)
    update_done_steel_by_month_only_F(count_date) # 皓民
    update_total_by_month(count_date.year,count_date.month) # 重新統計當月份總物料
