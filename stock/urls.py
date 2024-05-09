from django.urls import path

from stock.views import (
    RailControlView,
    RailDoneView,
    SteelControlView,
    SteelDoneView,
    get_rail_edit_done,
    get_steel_edit_done,
    rail_done_withdraw,
    steel_done_withdraw,
    steel_brace_view,
    steel_pile_view,
    ImportMaterialView,
    MaterialSeveView,
    MaterialsView,
    getMatrtialData,
    ImportConstnView,
    SiteViewList,
    StockView,
)
from stock.views.board_view import BoardControlView, get_board_edit_done
from stock.views.constn_view import component_view, constn_diff_view
from stock.views.materials_view import DownloadMaterialView
from stock.views.site_view import ConstnSeveView, ImportSiteInfoByTotalView
from stock.views.steel_view import get_edit_remark
from stock.views.stock_view import ConstnStockViewList

urlpatterns = [
    path("material/list/", MaterialsView.as_view(), name="material"),
    path(
        "material/uploadexcel/",
        ImportMaterialView.as_view(),
        name="material_uploadexcel",
    ),
    path(
        "material/download/",
        DownloadMaterialView.as_view(),
        name="material_uploadexcel",
    ),
    path("material/save/", MaterialSeveView.as_view(), name="material_sabe"),
    path("getMatrtialData/", getMatrtialData, name="carinfo"),
    path("stock/list/", StockView.as_view(), name="stock"),
    path("constn_stock/list/", ConstnStockViewList.as_view(), name="constn"),
    path("constn/list/", SiteViewList.as_view(), name="constn"),
    path("constn/edit/", ConstnSeveView.as_view(), name="construction_update"),
    path("constn/uploadexcel/", ImportConstnView.as_view(), name="constn"),
    path(
        "constn/uploadexcelByTotal/",
        ImportSiteInfoByTotalView.as_view(),
        name="material_uploadexcel",
    ),
    # path("split/material/", split_mat_constn, name="split_mat"),
    # path("steel_pile/", steel_pile, name="steel_pile"),
    path("rail_control/", RailControlView.as_view(), name="rail_control"),
    path("rail_control/edit/", get_rail_edit_done, name="rail_edit"),
    path("rail_done/", RailDoneView.as_view(), name="rail_done"),
    path("rail_done/withdraw/", rail_done_withdraw, name="rail_withdraw"),
    # path("rail_end/", rail_end, name="rail_end"),
    path("steel_control/", SteelControlView.as_view(), name="rail_control"),
    path("steel_control/edit/", get_steel_edit_done, name="rail_edit"),
    path("steel_done/", SteelDoneView.as_view(), name="rail_done"),
    path("steel_done/edit/", get_edit_remark, name="rail_withdraw"),
    path("steel_done/withdraw/", steel_done_withdraw, name="rail_withdraw"),
    path("board_report/", BoardControlView.as_view(), name="board_report"),
    path("board_report/edit/", get_board_edit_done, name="rail_edit"),
    path("constn/pile/", steel_pile_view, name="steel_pile_view"),
    path("constn/brace/", steel_brace_view, name="steel_brace_view"),
    path("constn/component/", component_view, name="component_view"),
    path("constn/constn_diff/", constn_diff_view, name="component_view"),
]
