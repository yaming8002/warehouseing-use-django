from django.urls import path

from w_whreport.views.board_view import BoardControlView, get_board_edit_done
from w_whreport.views.rail_view import RailControlView, RailDoneView, get_rail_edit_done, rail_done_withdraw
from w_whreport.views.steel_view import SteelControlView, SteelDoneView, get_add_remark, get_edit_remark, get_move_mat, get_steel_edit_done, steel_done_withdraw


urlpatterns = [
    path("rail_control/", RailControlView.as_view(), name="rail_control"),
    path("rail_control/edit/", get_rail_edit_done, name="rail_edit"),
    path("rail_done/", RailDoneView.as_view(), name="rail_done"),
    path("rail_done/withdraw/", rail_done_withdraw, name="rail_withdraw"),
    path("steel_control/", SteelControlView.as_view(), name="rail_control"),
    path("steel_control/edit/", get_steel_edit_done, name="rail_edit"),
    path("steel_control/move/", get_move_mat, name="rail_done"),
    path("steel_done/", SteelDoneView.as_view(), name="rail_done"),
    path("steel_done/add/", get_add_remark, name="rail_done"),
    path("steel_done/edit/", get_edit_remark, name="rail_withdraw"),
    path("steel_done/withdraw/", steel_done_withdraw, name="rail_withdraw"),
    path("board_report/", BoardControlView.as_view(), name="board_report"),
    path("board_report/edit/", get_board_edit_done, name="rail_edit")
]
