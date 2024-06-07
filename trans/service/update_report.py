

from trans.service.update_board_by_month import update_board_by_month
from trans.service.update_done_steel_by_month import update_done_steel_by_month, update_done_steel_by_month_only_F
from trans.service.update_rail_by_month import update_rail_by_month
from trans.service.update_steel_by_month import update_steel_by_month


def count_all_report(count_date):
    # update_rail_by_month(count_date)
    update_steel_by_month(count_date)
    # update_board_by_month(count_date)
    update_done_steel_by_month(count_date)
    update_done_steel_by_month_only_F(count_date)
