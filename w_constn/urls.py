from django.urls import path

from w_constn.views.constn_view import component_view, constn_diff_view, steel_brace_view, steel_control_item_check_view, steel_control_view, steel_pile_edit_view, steel_pile_view, tool_view
from w_constn.views.diff_report_view import report_download_by_month, report_download_by_site, report_end_view, report_remove, upload_pdf

urlpatterns = [
    path("constn/control/", steel_control_view, name="steel_control_view"),
    path("constn/control/item_check/", steel_control_item_check_view, name="steel_control_view"),
    path("constn/pile/", steel_pile_view, name="steel_pile_view"),
    path("constn/pile/edit/", steel_pile_edit_view, name="steel_brace_view"),
    path("constn/brace/", steel_brace_view, name="steel_brace_view"),
    path("constn/component/", component_view, name="component_view"),
    path("constn/tools/", tool_view, name="tool_view"),
    path("constn/constn_diff/", constn_diff_view, name="component_view"),
    path("constn/diff_report/upload/", upload_pdf, name="component_view"),
    path("constn/diff_report/", report_end_view, name="component_view"),
    path("constn/diff_report/donwload/", report_download_by_month, name="component_view"),
    path("constn/diff_report/donwload_by_site/<str:contsn_code>/", report_download_by_site, name="component_view"),
    path("constn/diff_report/remove/", report_remove, name="component_view"),
]
