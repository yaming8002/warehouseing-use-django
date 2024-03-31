from django.urls import path

from report.views import (
    RailControlView,
    RailDoneView,
    SteelControlView,
    SteelDoneView,
    get_rail_edit_done,
    get_steel_edit_done,
    rail_done_withdraw,
    steel_done_withdraw,
    steel_brace_view,
    steel_pile_view
)



urlpatterns = [
    # path("steel_pile/", steel_pile, name="steel_pile"),
    path("rail_control/", RailControlView.as_view(), name="rail_control"),
    path("rail_control/edit/", get_rail_edit_done, name="rail_edit"),
    path("rail_done/", RailDoneView.as_view(), name="rail_done"),
    path("rail_done/withdraw/", rail_done_withdraw, name="rail_withdraw"),


    # path("rail_end/", rail_end, name="rail_end"),
    path("steel_control/", SteelControlView.as_view(), name="rail_control"),
    path("steel_control/edit/", get_steel_edit_done, name="rail_edit"),
    path("steel_done/", SteelDoneView.as_view(), name="rail_done"),
    path("steel_done/withdraw/", steel_done_withdraw, name="rail_withdraw"),

    path("constn/pile/", steel_pile_view, name="steel_pile_view"),
    path("constn/brace/", steel_brace_view, name="steel_brace_view"),


]
